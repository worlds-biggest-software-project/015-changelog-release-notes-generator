# Data Model Suggestion 2: Event-Sourced / Audit-First

> Project: Changelog & Release Notes Generator · Created: 2026-05-11

## Philosophy

This model treats every state change as an immutable event stored in a central event store. Rather than updating rows in place, the system appends events like `CommitIngested`, `CommitClassified`, `ReleaseCreated`, `EntryGenerated`, and `EntryPublished`. The current state of any entity is derived by replaying its event stream. Materialized read models (CQRS pattern) are projected from the event store to serve queries efficiently.

This architecture is directly inspired by the audit trail requirements identified in the features survey: "engineering managers and compliance officers need traceability from release notes back to specific commits, PRs, and tickets." Event sourcing provides this traceability by default — the entire history of how a changelog entry was created, classified, edited, and published is preserved as a sequence of events. You can answer questions like "what was the classification of this commit before the AI model was upgraded?" or "when did this entry move from draft to published?" without any additional audit logging.

The CQRS separation also maps naturally to the changelog generator's read/write asymmetry: writes happen in bursts (ingesting a batch of commits when preparing a release), while reads are continuous and varied (rendering changelogs for different audiences, querying release history, generating cross-release summaries).

**Best for:** Regulated environments requiring full audit trails, teams that need temporal queries ("what did release notes look like at time T?"), and systems where AI classification may be re-run or improved over time and historical decisions must be preserved.

**Trade-offs:**
- (+) Complete, immutable audit trail — every change is recorded with timestamp and actor
- (+) Temporal queries are trivial — replay events up to any point in time
- (+) AI re-classification preserves history — old and new classifications coexist as events
- (+) Natural fit for CQRS — optimized read models for different audiences
- (+) Event replay enables rebuilding read models when requirements change
- (-) Higher implementation complexity — requires event store + projection infrastructure
- (-) Eventual consistency between event store and read models
- (-) More storage required — events accumulate; need archival strategy
- (-) Debugging requires understanding event replay, not just inspecting current state
- (-) Queries against the event store directly are expensive; must use projections

---

## Standards Alignment

| Standard | How It's Used |
|----------|---------------|
| Conventional Commits v1.0.0 | `CommitClassified` event payload includes type, scope, and breaking flag per the specification |
| Semantic Versioning 2.0.0 | `ReleaseCreated` event captures decomposed SemVer fields; `VersionBumpCalculated` event records the reasoning |
| Keep a Changelog v1.1.0 | Read model `release_view` materializes entries in canonical KaC categories |
| ISO 8601 | All event timestamps use ISO 8601 with timezone; release dates stored as ISO 8601 dates |
| CommonMark 0.31.2 | Event payloads store markdown content in CommonMark format |
| OCSF (Open Cybersecurity Schema Framework) | Event structure follows OCSF patterns: `event_type`, `actor`, `timestamp`, `payload` |
| CloudEvents v1.0.4 | Event envelope follows CloudEvents specification for interoperability |

---

## Event Store

```sql
-- The immutable event store — single source of truth
-- Every state change in the system is recorded here
CREATE TABLE events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stream_id       UUID NOT NULL,                   -- aggregate root ID (repository, release, entry, etc.)
    stream_type     TEXT NOT NULL,                    -- 'repository', 'commit', 'release', 'entry', 'publication'
    event_type      TEXT NOT NULL,                    -- e.g. 'CommitIngested', 'CommitClassified', 'ReleaseCreated'
    event_version   INTEGER NOT NULL,                 -- schema version of this event type (for evolution)
    sequence_number BIGINT NOT NULL,                  -- monotonically increasing within a stream
    payload         JSONB NOT NULL,                   -- event-specific data
    metadata        JSONB NOT NULL DEFAULT '{}',      -- actor, correlation_id, causation_id, ai_model, etc.
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (stream_id, sequence_number)
);

-- Global ordering for projections that need cross-stream consistency
CREATE SEQUENCE events_global_seq;
ALTER TABLE events ADD COLUMN global_position BIGINT NOT NULL DEFAULT nextval('events_global_seq');

CREATE INDEX idx_events_stream ON events(stream_id, sequence_number);
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_occurred ON events(occurred_at);
CREATE INDEX idx_events_global ON events(global_position);
CREATE INDEX idx_events_stream_type ON events(stream_type, event_type);

-- Projection checkpoints — tracks where each read model has consumed up to
CREATE TABLE projection_checkpoints (
    projection_name TEXT PRIMARY KEY,
    last_global_position BIGINT NOT NULL DEFAULT 0,
    last_updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### Event Type Catalog

```sql
-- Reference table documenting all known event types and their payload schemas
CREATE TABLE event_type_registry (
    event_type      TEXT PRIMARY KEY,
    stream_type     TEXT NOT NULL,
    current_version INTEGER NOT NULL DEFAULT 1,
    payload_schema  JSONB NOT NULL,                   -- JSON Schema for the payload
    description     TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### Core Event Types and Payloads

**Repository events:**
```
-- RepositoryRegistered
-- payload: {"name": "my-org/my-repo", "provider": "github", "clone_url": "...", "api_url": "...", "is_monorepo": false}

-- RepositoryConfigUpdated
-- payload: {"llm_provider": "anthropic", "llm_model": "claude-3.5-sonnet", "commit_filter_patterns": ["^Merge"]}

-- ProviderConnected
-- payload: {"provider": "jira", "api_base_url": "https://company.atlassian.net", "project_key": "MYAPP"}
```

**Commit events:**
```
-- CommitIngested
-- payload: {"sha": "abc123", "repository_id": "...", "author_email": "dev@example.com",
--           "author_name": "Dev", "message_subject": "Add user auth", "message_body": "...",
--           "committed_at": "2026-05-10T14:30:00Z", "files_changed": 5, "insertions": 120, "deletions": 30}

-- CommitClassified
-- payload: {"commit_sha": "abc123", "type": "feat", "scope": "auth", "is_breaking": false,
--           "is_internal": false, "confidence": 0.94, "method": "ai_llm",
--           "user_impact_summary": "Users can now log in with SSO",
--           "developer_summary": "Implement OIDC auth flow with PKCE"}

-- CommitReclassified
-- payload: {"commit_sha": "abc123", "previous_type": "chore", "new_type": "feat",
--           "reason": "AI model upgrade from v1 to v2", "confidence": 0.97, "method": "ai_llm"}
```

**Pull Request events:**
```
-- PullRequestIngested
-- payload: {"provider_pr_id": "42", "repository_id": "...", "title": "Add SSO login",
--           "body": "Implements OIDC-based SSO...", "author_email": "dev@example.com",
--           "state": "merged", "merged_at": "2026-05-10T16:00:00Z", "labels": ["feature"],
--           "linked_commit_shas": ["abc123", "def456"],
--           "linked_issue_ids": ["MYAPP-789"]}
```

**Issue events:**
```
-- IssueIngested
-- payload: {"provider": "jira", "provider_issue_id": "MYAPP-789", "repository_id": "...",
--           "title": "SSO Login Support", "body": "As a user, I want to log in with my company SSO...",
--           "status": "done", "issue_type": "story", "priority": "high", "fix_version": "1.3.0"}
```

**Release events:**
```
-- ReleaseCreated
-- payload: {"repository_id": "...", "tag_name": "v1.3.0", "version_major": 1, "version_minor": 3,
--           "version_patch": 0, "release_date": "2026-05-11", "from_sha": "prev_tag_sha",
--           "to_sha": "v1.3.0_sha"}

-- VersionBumpCalculated
-- payload: {"repository_id": "...", "previous_version": "1.2.5", "new_version": "1.3.0",
--           "bump_type": "minor", "reason": "feat commits detected; no breaking changes",
--           "contributing_commits": ["abc123", "ghi789"]}

-- ReleasePublished
-- payload: {"release_id": "...", "channel": "github_release", "provider_release_id": "12345",
--           "provider_release_url": "https://github.com/my-org/my-repo/releases/tag/v1.3.0"}

-- ReleaseYanked
-- payload: {"release_id": "...", "reason": "Critical security issue found in auth module"}
```

**Changelog Entry events:**
```
-- EntryGenerated
-- payload: {"release_id": "...", "category": "Added", "body_markdown": "SSO login support via OIDC",
--           "is_breaking": false, "source_commit_shas": ["abc123"],
--           "source_pr_ids": ["42"], "source_issue_ids": ["MYAPP-789"],
--           "generation_method": "ai_generated", "ai_model": "claude-3.5-sonnet"}

-- EntryEdited
-- payload: {"entry_id": "...", "previous_body": "SSO login support via OIDC",
--           "new_body": "Single Sign-On (SSO) login support via OpenID Connect",
--           "edited_by": "user@example.com", "reason": "Clarified acronym"}

-- AudienceVariantGenerated
-- payload: {"entry_id": "...", "audience": "end_user",
--           "body_markdown": "You can now log in with your company credentials — no separate password needed!",
--           "is_visible": true, "generation_method": "ai_generated"}

-- AudienceVariantGenerated
-- payload: {"entry_id": "...", "audience": "developer",
--           "body_markdown": "Implement OIDC Authorization Code flow with PKCE for SSO integration. New env vars: `OIDC_CLIENT_ID`, `OIDC_ISSUER_URL`.",
--           "is_visible": true, "generation_method": "ai_generated"}
```

---

## Materialized Read Models (CQRS Projections)

These tables are derived from the event store and can be rebuilt at any time by replaying events.

```sql
-- ============================================================
-- READ MODEL: Repository Overview
-- Projected from: RepositoryRegistered, RepositoryConfigUpdated
-- ============================================================
CREATE TABLE repo_view (
    id              UUID PRIMARY KEY,
    name            TEXT NOT NULL,
    provider        TEXT NOT NULL,
    clone_url       TEXT,
    api_url         TEXT,
    is_monorepo     BOOLEAN NOT NULL DEFAULT FALSE,
    llm_provider    TEXT,
    llm_model       TEXT,
    commit_filter_patterns TEXT[],
    connected_providers TEXT[],                        -- ['github', 'jira', 'linear']
    total_commits   INTEGER NOT NULL DEFAULT 0,
    total_releases  INTEGER NOT NULL DEFAULT 0,
    latest_release_tag TEXT,
    latest_release_date DATE,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- READ MODEL: Commit with Classification
-- Projected from: CommitIngested, CommitClassified, CommitReclassified
-- ============================================================
CREATE TABLE commit_view (
    id              UUID PRIMARY KEY,                 -- same as stream_id for this commit
    repository_id   UUID NOT NULL,
    sha             TEXT NOT NULL,
    author_name     TEXT,
    author_email    TEXT,
    message_subject TEXT NOT NULL,
    message_body    TEXT,
    committed_at    TIMESTAMPTZ NOT NULL,
    files_changed   INTEGER,
    insertions      INTEGER,
    deletions       INTEGER,
    -- Classification (latest)
    classified_type TEXT,                              -- 'feat', 'fix', etc.
    classified_scope TEXT,
    is_breaking     BOOLEAN DEFAULT FALSE,
    is_internal     BOOLEAN DEFAULT FALSE,
    classification_confidence REAL,
    classification_method TEXT,
    user_impact_summary TEXT,
    developer_summary TEXT,
    -- Linkage
    pull_request_ids UUID[],
    issue_ids       UUID[],
    release_id      UUID,                             -- set when assigned to a release
    classification_count INTEGER DEFAULT 0,           -- how many times classified/reclassified
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_commit_view_repo ON commit_view(repository_id, committed_at DESC);
CREATE INDEX idx_commit_view_sha ON commit_view(sha);
CREATE INDEX idx_commit_view_type ON commit_view(classified_type);
CREATE INDEX idx_commit_view_unassigned ON commit_view(repository_id)
    WHERE release_id IS NULL;

-- ============================================================
-- READ MODEL: Release with Entries and Variants
-- Projected from: ReleaseCreated, EntryGenerated, AudienceVariantGenerated, ReleasePublished, ReleaseYanked
-- ============================================================
CREATE TABLE release_view (
    id              UUID PRIMARY KEY,
    repository_id   UUID NOT NULL,
    tag_name        TEXT NOT NULL,
    version_major   INTEGER NOT NULL,
    version_minor   INTEGER NOT NULL,
    version_patch   INTEGER NOT NULL,
    version_prerelease TEXT,
    release_date    DATE NOT NULL,
    title           TEXT,
    is_draft        BOOLEAN NOT NULL DEFAULT FALSE,
    is_prerelease   BOOLEAN NOT NULL DEFAULT FALSE,
    is_yanked       BOOLEAN NOT NULL DEFAULT FALSE,
    is_published    BOOLEAN NOT NULL DEFAULT FALSE,
    published_channels TEXT[],                        -- ['github_release', 'slack']
    total_entries   INTEGER NOT NULL DEFAULT 0,
    breaking_count  INTEGER NOT NULL DEFAULT 0,
    commit_count    INTEGER NOT NULL DEFAULT 0,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE release_entry_view (
    id              UUID PRIMARY KEY,
    release_id      UUID NOT NULL REFERENCES release_view(id),
    category        TEXT NOT NULL,                    -- 'Added', 'Changed', etc.
    body_markdown   TEXT NOT NULL,
    display_order   INTEGER NOT NULL DEFAULT 0,
    is_breaking     BOOLEAN NOT NULL DEFAULT FALSE,
    is_security     BOOLEAN NOT NULL DEFAULT FALSE,
    source_commit_shas TEXT[],
    source_pr_ids   TEXT[],
    source_issue_ids TEXT[],
    generation_method TEXT NOT NULL,
    ai_model        TEXT,
    edit_count      INTEGER NOT NULL DEFAULT 0,       -- tracked via EntryEdited events
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE entry_variant_view (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entry_id        UUID NOT NULL REFERENCES release_entry_view(id),
    audience        TEXT NOT NULL,                    -- 'developer', 'end_user', 'admin'
    body_markdown   TEXT NOT NULL,
    is_visible      BOOLEAN NOT NULL DEFAULT TRUE,
    generation_method TEXT NOT NULL,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (entry_id, audience)
);

CREATE INDEX idx_release_view_repo ON release_view(repository_id, release_date DESC);
CREATE INDEX idx_release_entry_view_release ON release_entry_view(release_id, display_order);
CREATE INDEX idx_entry_variant_view_entry ON entry_variant_view(entry_id);

-- ============================================================
-- READ MODEL: Audit Timeline
-- A flattened, human-readable audit log projected from ALL events
-- ============================================================
CREATE TABLE audit_timeline_view (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id        UUID NOT NULL,                    -- reference back to events table
    global_position BIGINT NOT NULL,
    occurred_at     TIMESTAMPTZ NOT NULL,
    stream_type     TEXT NOT NULL,
    stream_id       UUID NOT NULL,
    event_type      TEXT NOT NULL,
    actor           TEXT,                             -- who/what caused this event
    summary         TEXT NOT NULL,                    -- human-readable one-liner
    related_release_id UUID,                          -- for filtering by release
    related_repository_id UUID                        -- for filtering by repository
);

CREATE INDEX idx_audit_timeline_occurred ON audit_timeline_view(occurred_at DESC);
CREATE INDEX idx_audit_timeline_release ON audit_timeline_view(related_release_id);
CREATE INDEX idx_audit_timeline_repo ON audit_timeline_view(related_repository_id);
CREATE INDEX idx_audit_timeline_type ON audit_timeline_view(event_type);
```

---

## Snapshot Support

```sql
-- Periodic snapshots to avoid replaying full event history
CREATE TABLE snapshots (
    stream_id       UUID NOT NULL,
    stream_type     TEXT NOT NULL,
    sequence_number BIGINT NOT NULL,                  -- event sequence at which snapshot was taken
    state           JSONB NOT NULL,                   -- serialized aggregate state
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (stream_id, sequence_number)
);

CREATE INDEX idx_snapshots_latest ON snapshots(stream_id, sequence_number DESC);
```

---

## Table Count Summary

| Category | Tables | Notes |
|----------|--------|-------|
| Event Store | 3 | events, projection_checkpoints, event_type_registry |
| Read Model: Repositories | 1 | repo_view |
| Read Model: Commits | 1 | commit_view (denormalized with classification) |
| Read Model: Releases | 3 | release_view, release_entry_view, entry_variant_view |
| Read Model: Audit | 1 | audit_timeline_view |
| Snapshots | 1 | snapshots |
| **Total** | **10** | Plus the events table which stores all state |

---

## Key Design Decisions

1. **Single `events` table as source of truth** — all state derives from this table. The `stream_id` + `sequence_number` pair provides per-aggregate ordering, while `global_position` provides cross-aggregate ordering for projections. This follows the standard event sourcing pattern described by Martin Fowler and implemented by EventStoreDB.

2. **JSONB `payload` with versioned schemas** — the `event_version` field enables event schema evolution. When the payload structure changes, a new version is introduced and upcasters transform old events to the new schema during replay. This avoids destructive migrations.

3. **Separate `CommitClassified` and `CommitReclassified` events** — when the AI model is upgraded or classification is re-run, the system emits `CommitReclassified` rather than overwriting. Both the old and new classifications are preserved in the event history, enabling analysis of AI improvement over time.

4. **Materialized read models are disposable** — every `*_view` table can be dropped and rebuilt by replaying events from the store. This means the read schema can evolve freely without data migrations — just update the projection code and rebuild.

5. **`audit_timeline_view` as a human-readable projection** — rather than requiring users to parse raw JSONB events, this projection flattens events into a timeline with human-readable summaries. Filtered by release or repository for compliance reporting.

6. **Snapshots for performance** — for aggregates with long event histories (e.g., a repository with 10,000+ commits), periodic snapshots avoid replaying the full event stream. Load snapshot, then replay only events after the snapshot's sequence number.

7. **`metadata` field on events captures actor and correlation** — every event records who/what caused it (user, CI pipeline, AI model) and a `correlation_id` linking related events across aggregates (e.g., all events triggered by a single "generate release" command share one correlation ID).

8. **CloudEvents-inspired envelope** — the event structure follows CloudEvents v1.0.4 patterns (`type`, `source`, `time`, `data`) for potential interoperability with external event systems, webhooks, and message brokers.

9. **No foreign keys on read models** — read model tables reference each other for query convenience but do not enforce FK constraints. They are projections, not sources of truth; consistency is guaranteed by the event store and projection logic, not by the database.

10. **`classification_count` on `commit_view`** tracks how many times a commit has been classified or reclassified, providing a quick signal for AI quality monitoring without querying the event store.

---

## Example Queries

### Replay commit classification history
```sql
-- Show how a commit's classification changed over time
SELECT e.occurred_at,
       e.event_type,
       e.payload->>'type' AS classified_type,
       e.payload->>'confidence' AS confidence,
       e.payload->>'method' AS method,
       e.metadata->>'ai_model' AS ai_model
FROM events e
WHERE e.stream_id = (SELECT id FROM commit_view WHERE sha = $1)
  AND e.event_type IN ('CommitClassified', 'CommitReclassified')
ORDER BY e.sequence_number;
```

### Full audit trail for a release
```sql
-- Every event related to a specific release, in order
SELECT at.occurred_at, at.event_type, at.actor, at.summary
FROM audit_timeline_view at
WHERE at.related_release_id = $1
ORDER BY at.global_position;
```

### Point-in-time release notes (what did the release look like at time T?)
```sql
-- Reconstruct release state at a specific point in time
-- by reading events up to that timestamp
SELECT e.event_type, e.payload, e.occurred_at
FROM events e
WHERE e.stream_id = $1          -- release stream ID
  AND e.occurred_at <= $2       -- point in time
ORDER BY e.sequence_number;
-- Application code replays these events to build the state
```

### Commits awaiting classification
```sql
SELECT cv.sha, cv.message_subject, cv.committed_at
FROM commit_view cv
WHERE cv.repository_id = $1
  AND cv.classified_type IS NULL
ORDER BY cv.committed_at;
```

### AI classification accuracy trend
```sql
-- Average confidence of AI classifications over time, grouped by month
SELECT date_trunc('month', e.occurred_at) AS month,
       AVG((e.payload->>'confidence')::real) AS avg_confidence,
       COUNT(*) AS classification_count
FROM events e
WHERE e.event_type = 'CommitClassified'
  AND e.payload->>'method' = 'ai_llm'
GROUP BY 1
ORDER BY 1;
```
