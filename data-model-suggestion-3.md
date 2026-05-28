# Data Model Suggestion 3: Hybrid Relational + JSONB

> Project: Changelog & Release Notes Generator · Created: 2026-05-11

## Philosophy

This model uses relational tables for core entities with well-defined schemas (repositories, releases, entries) while leveraging PostgreSQL JSONB columns for data that varies by provider, audience, or configuration. The key insight is that a changelog generator must integrate with multiple external systems (GitHub, GitLab, Jira, Linear), each with different data shapes, and the metadata attached to commits, PRs, and issues varies wildly between providers and even between projects on the same provider.

Rather than creating provider-specific columns (e.g., `github_pr_number`, `gitlab_mr_iid`, `jira_issue_key`) or complex inheritance hierarchies, this model stores the stable, queryable core fields as typed columns and pushes variable/provider-specific data into JSONB columns with GIN indexes. This is the pattern recommended by Citus/Microsoft for multi-tenant SaaS applications and used by platforms like Notion and Linear internally.

The hybrid approach also fits the AI generation workflow well: LLM outputs (classifications, summaries, variant texts) have evolving schemas as prompts improve. Storing AI outputs in JSONB avoids constant migrations while keeping the core release/entry structure stable and queryable.

**Best for:** Rapid MVP development, teams integrating multiple git/issue providers, projects where the metadata schema evolves frequently, and deployments where a single PostgreSQL instance is preferred over a multi-database architecture.

**Trade-offs:**
- (+) Fewer tables (~14 vs. 23 in the normalized model) — simpler to deploy and manage
- (+) Provider-specific data stored without schema migrations — add a new provider by writing different JSONB
- (+) AI output schema can evolve without database migrations
- (+) JSONB GIN indexes enable fast queries on variable metadata
- (+) Single PostgreSQL instance — no event store infrastructure needed
- (+) Rapid iteration — change what you store without ALTER TABLE
- (-) JSONB fields lack compile-time type safety — validation moves to application layer
- (-) Complex JSONB queries can be harder to optimize than normalized JOINs
- (-) No automatic referential integrity for data inside JSONB columns
- (-) JSONB storage is less space-efficient than typed columns for high-volume fields
- (-) Audit trail requires explicit implementation (not built-in like event sourcing)

---

## Standards Alignment

| Standard | How It's Used |
|----------|---------------|
| Conventional Commits v1.0.0 | `commits.classification` JSONB stores type/scope/breaking per the specification vocabulary |
| Semantic Versioning 2.0.0 | `releases.version` JSONB decomposes SemVer into `{major, minor, patch, prerelease, build_metadata}` |
| Keep a Changelog v1.1.0 | `changelog_entries.category` uses the six canonical categories; output templates follow KaC format |
| ISO 8601 | All timestamps as `TIMESTAMPTZ`; dates as ISO 8601 strings in JSONB where needed |
| CommonMark 0.31.2 | `changelog_entries.body_markdown` and `audience_variants` JSONB store CommonMark content |
| JSON Schema | JSONB columns validated against JSON Schemas defined in the application layer |
| OAuth 2.0 (RFC 6749) | `repositories.provider_config` JSONB stores OAuth tokens per provider |
| GDPR (EU 2016/679) | `commits.author_info` JSONB can be selectively scrubbed without affecting commit metadata |

---

## Core Tables

```sql
-- ============================================================
-- REPOSITORIES
-- Core fields are relational; provider-specific config in JSONB
-- ============================================================
CREATE TABLE repositories (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,                    -- e.g. "my-org/my-repo"
    provider        TEXT NOT NULL CHECK (provider IN ('github', 'gitlab', 'bitbucket', 'local')),
    default_branch  TEXT NOT NULL DEFAULT 'main',
    is_monorepo     BOOLEAN NOT NULL DEFAULT FALSE,

    -- Provider-specific configuration and connection details
    provider_config JSONB NOT NULL DEFAULT '{}',
    -- GitHub example:
    -- {
    --   "repo_id": 123456789,
    --   "clone_url": "https://github.com/my-org/my-repo.git",
    --   "api_url": "https://api.github.com/repos/my-org/my-repo",
    --   "access_token": "ghp_...",        -- encrypted at rest
    --   "webhook_secret": "whsec_..."
    -- }
    -- GitLab example:
    -- {
    --   "project_id": 42,
    --   "clone_url": "https://gitlab.com/my-org/my-repo.git",
    --   "api_url": "https://gitlab.com/api/v4/projects/42",
    --   "access_token": "glpat-...",
    --   "ci_job_token": true
    -- }

    -- Issue tracker connections (can connect to multiple)
    issue_trackers  JSONB NOT NULL DEFAULT '[]',
    -- [
    --   {
    --     "provider": "jira",
    --     "api_base_url": "https://company.atlassian.net",
    --     "project_key": "MYAPP",
    --     "access_token": "...",
    --     "issue_pattern": "MYAPP-\\d+"
    --   },
    --   {
    --     "provider": "linear",
    --     "api_url": "https://api.linear.app/graphql",
    --     "api_key": "lin_...",
    --     "team_key": "ENG"
    --   }
    -- ]

    -- Generator configuration
    generator_config JSONB NOT NULL DEFAULT '{}',
    -- {
    --   "llm_provider": "anthropic",
    --   "llm_model": "claude-3.5-sonnet",
    --   "commit_filter_patterns": ["^Merge", "^chore\\(deps\\)"],
    --   "include_contributors": true,
    --   "include_pr_links": true,
    --   "version_scheme": "semver",
    --   "audiences": ["developer", "end_user", "admin"],
    --   "default_template": "keep-a-changelog"
    -- }

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (provider, name)
);

-- Packages within monorepos
CREATE TABLE packages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id   UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    path            TEXT NOT NULL,
    package_config  JSONB NOT NULL DEFAULT '{}',
    -- {
    --   "publish_to": "npm",
    --   "changelog_path": "packages/core/CHANGELOG.md",
    --   "version_independent": true
    -- }
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (repository_id, name)
);

CREATE INDEX idx_repositories_provider ON repositories(provider);
CREATE INDEX idx_repositories_provider_config ON repositories USING GIN (provider_config);
CREATE INDEX idx_packages_repository ON packages(repository_id);
```

---

## Commits

```sql
-- ============================================================
-- COMMITS
-- Core git fields are relational; classification and provider
-- metadata in JSONB
-- ============================================================
CREATE TABLE commits (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id   UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    sha             TEXT NOT NULL,
    message_subject TEXT NOT NULL,
    message_body    TEXT,
    committed_at    TIMESTAMPTZ NOT NULL,
    is_merge_commit BOOLEAN NOT NULL DEFAULT FALSE,

    -- Author info (JSONB for GDPR-compliant selective scrubbing)
    author_info     JSONB NOT NULL DEFAULT '{}',
    -- {
    --   "name": "Jane Developer",
    --   "email": "jane@example.com",
    --   "provider_username": "jane-dev",
    --   "provider_user_id": "12345",
    --   "avatar_url": "https://avatars.githubusercontent.com/u/12345"
    -- }
    -- After GDPR erasure:
    -- {"gdpr_erased": true, "erased_at": "2026-05-11T00:00:00Z"}

    -- Diff statistics
    diff_stats      JSONB,
    -- {
    --   "files_changed": 5,
    --   "insertions": 120,
    --   "deletions": 30,
    --   "files": [
    --     {"path": "src/auth/oidc.ts", "insertions": 80, "deletions": 5},
    --     {"path": "src/auth/index.ts", "insertions": 40, "deletions": 25}
    --   ]
    -- }

    -- AI/rule-based classification result
    classification  JSONB,
    -- {
    --   "type": "feat",
    --   "scope": "auth",
    --   "is_breaking": false,
    --   "is_internal": false,
    --   "confidence": 0.94,
    --   "method": "ai_llm",
    --   "model": "claude-3.5-sonnet",
    --   "classified_at": "2026-05-11T10:30:00Z",
    --   "user_impact_summary": "Users can now log in with SSO",
    --   "developer_summary": "Implement OIDC auth flow with PKCE",
    --   "previous_classifications": [
    --     {"type": "chore", "confidence": 0.62, "method": "ai_llm", "model": "claude-3-haiku", "classified_at": "2026-04-01T..."}
    --   ]
    -- }

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (repository_id, sha)
);

CREATE INDEX idx_commits_repo_date ON commits(repository_id, committed_at DESC);
CREATE INDEX idx_commits_sha ON commits(sha);
CREATE INDEX idx_commits_classification_type ON commits USING GIN (classification jsonb_path_ops);
-- Enables queries like: WHERE classification @> '{"type": "feat"}'
-- and: WHERE classification @> '{"is_breaking": true}'
```

---

## Pull Requests & Issues

```sql
-- ============================================================
-- SOURCE ITEMS
-- Unified table for PRs, issues, and tickets from all providers
-- Provider-specific fields stored in JSONB metadata
-- ============================================================
CREATE TABLE source_items (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id   UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    item_type       TEXT NOT NULL CHECK (item_type IN ('pull_request', 'issue', 'ticket')),
    provider        TEXT NOT NULL CHECK (provider IN ('github', 'gitlab', 'jira', 'linear')),
    provider_item_id TEXT NOT NULL,                   -- "42" (PR#), "MYAPP-789" (Jira), etc.
    title           TEXT NOT NULL,
    body            TEXT,
    status          TEXT NOT NULL,                    -- 'open', 'closed', 'merged', 'done', etc.

    -- Author info (same JSONB structure as commits)
    author_info     JSONB NOT NULL DEFAULT '{}',

    -- Provider-specific metadata
    metadata        JSONB NOT NULL DEFAULT '{}',
    -- Pull request example:
    -- {
    --   "state": "merged",
    --   "merged_at": "2026-05-10T16:00:00Z",
    --   "labels": ["feature", "auth"],
    --   "reviewers": ["alice", "bob"],
    --   "html_url": "https://github.com/my-org/my-repo/pull/42",
    --   "base_branch": "main",
    --   "head_branch": "feat/sso-login",
    --   "commits_count": 3
    -- }
    -- Jira issue example:
    -- {
    --   "issue_type": "story",
    --   "priority": "high",
    --   "labels": ["auth", "sso"],
    --   "fix_version": "1.3.0",
    --   "epic_key": "MYAPP-500",
    --   "story_points": 5,
    --   "sprint": "Sprint 42",
    --   "html_url": "https://company.atlassian.net/browse/MYAPP-789",
    --   "acceptance_criteria": "User can log in via company OIDC provider"
    -- }
    -- Linear issue example:
    -- {
    --   "identifier": "ENG-123",
    --   "state": "done",
    --   "priority": 1,
    --   "labels": ["feature"],
    --   "project": "Auth Improvements",
    --   "cycle": "Cycle 12",
    --   "estimate": 3
    -- }

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (repository_id, provider, item_type, provider_item_id)
);

-- Linkage between commits and source items (PRs, issues, tickets)
CREATE TABLE commit_source_links (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    commit_id       UUID NOT NULL REFERENCES commits(id) ON DELETE CASCADE,
    source_item_id  UUID NOT NULL REFERENCES source_items(id) ON DELETE CASCADE,
    link_type       TEXT NOT NULL CHECK (link_type IN ('authored_in', 'fixes', 'references', 'closes')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (commit_id, source_item_id, link_type)
);

CREATE INDEX idx_source_items_repo ON source_items(repository_id, item_type);
CREATE INDEX idx_source_items_provider ON source_items(provider, provider_item_id);
CREATE INDEX idx_source_items_metadata ON source_items USING GIN (metadata jsonb_path_ops);
-- Enables: WHERE metadata @> '{"fix_version": "1.3.0"}'
-- Enables: WHERE metadata @> '{"labels": ["auth"]}'
CREATE INDEX idx_commit_source_links_commit ON commit_source_links(commit_id);
CREATE INDEX idx_commit_source_links_source ON commit_source_links(source_item_id);
```

---

## Releases & Changelog Entries

```sql
-- ============================================================
-- RELEASES
-- Core version fields are relational; distribution status in JSONB
-- ============================================================
CREATE TABLE releases (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id   UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    package_id      UUID REFERENCES packages(id) ON DELETE CASCADE,
    tag_name        TEXT NOT NULL,

    -- Decomposed version for efficient range queries
    version         JSONB NOT NULL,
    -- {
    --   "major": 1, "minor": 3, "patch": 0,
    --   "prerelease": null,
    --   "build_metadata": null,
    --   "scheme": "semver",
    --   "raw": "1.3.0"
    -- }

    release_date    DATE NOT NULL,
    title           TEXT,
    status          TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'yanked')),
    is_prerelease   BOOLEAN NOT NULL DEFAULT FALSE,

    -- Commit range this release covers
    commit_range    JSONB NOT NULL,
    -- {
    --   "from_sha": "abc123",  -- exclusive (previous release tag)
    --   "to_sha": "def456",    -- inclusive (this release tag)
    --   "commit_count": 47,
    --   "first_commit_date": "2026-04-15T...",
    --   "last_commit_date": "2026-05-10T..."
    -- }

    -- Version bump reasoning (AI or rule-based)
    version_decision JSONB,
    -- {
    --   "previous_version": "1.2.5",
    --   "bump_type": "minor",
    --   "reason": "feat commits detected; no breaking changes",
    --   "method": "ai_llm",
    --   "contributing_types": {"feat": 3, "fix": 8, "chore": 12}
    -- }

    -- Publication status across channels
    publications    JSONB NOT NULL DEFAULT '[]',
    -- [
    --   {
    --     "channel": "github_release",
    --     "status": "published",
    --     "published_at": "2026-05-11T12:00:00Z",
    --     "provider_release_id": "12345",
    --     "url": "https://github.com/my-org/my-repo/releases/tag/v1.3.0"
    --   },
    --   {
    --     "channel": "slack",
    --     "status": "published",
    --     "published_at": "2026-05-11T12:01:00Z",
    --     "webhook_response": {"ok": true}
    --   },
    --   {
    --     "channel": "changelog_file",
    --     "status": "published",
    --     "published_at": "2026-05-11T12:02:00Z",
    --     "file_path": "CHANGELOG.md",
    --     "commit_sha": "xyz789"
    --   }
    -- ]

    -- Summary statistics (denormalized for dashboard queries)
    stats           JSONB NOT NULL DEFAULT '{}',
    -- {
    --   "total_entries": 15,
    --   "breaking_changes": 0,
    --   "features": 3,
    --   "fixes": 8,
    --   "other": 4,
    --   "contributors": ["jane-dev", "bob-eng", "alice-pm"],
    --   "contributor_count": 3
    -- }

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (repository_id, tag_name)
);

-- ============================================================
-- CHANGELOG ENTRIES
-- Core fields relational; audience variants and source tracing in JSONB
-- ============================================================
CREATE TABLE changelog_entries (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    release_id      UUID NOT NULL REFERENCES releases(id) ON DELETE CASCADE,
    category        TEXT NOT NULL,                    -- 'Added', 'Changed', 'Deprecated', 'Removed', 'Fixed', 'Security'
    body_markdown   TEXT NOT NULL,                    -- default/developer-facing CommonMark content
    display_order   INTEGER NOT NULL DEFAULT 0,
    is_breaking     BOOLEAN NOT NULL DEFAULT FALSE,
    is_security     BOOLEAN NOT NULL DEFAULT FALSE,
    is_highlight    BOOLEAN NOT NULL DEFAULT FALSE,

    -- Source traceability (which commits/PRs/issues produced this entry)
    sources         JSONB NOT NULL DEFAULT '{}',
    -- {
    --   "commit_shas": ["abc123", "def456"],
    --   "pull_request_ids": ["42"],
    --   "issue_ids": ["MYAPP-789"],
    --   "commit_ids": ["<uuid>", "<uuid>"],          -- internal UUIDs
    --   "source_item_ids": ["<uuid>", "<uuid>"]      -- internal UUIDs
    -- }

    -- AI generation metadata
    generation      JSONB NOT NULL DEFAULT '{}',
    -- {
    --   "method": "ai_generated",
    --   "model": "claude-3.5-sonnet",
    --   "prompt_hash": "sha256:...",
    --   "generated_at": "2026-05-11T10:45:00Z",
    --   "confidence": 0.91,
    --   "edited_by_human": false,
    --   "edit_history": [
    --     {"at": "2026-05-11T11:00:00Z", "by": "user@example.com", "previous_body": "..."}
    --   ]
    -- }

    -- Audience-specific variants stored inline
    audience_variants JSONB NOT NULL DEFAULT '{}',
    -- {
    --   "end_user": {
    --     "body_markdown": "You can now log in with your company credentials!",
    --     "is_visible": true,
    --     "generated_at": "2026-05-11T10:46:00Z"
    --   },
    --   "admin": {
    --     "body_markdown": "New SSO integration via OIDC. Configure with OIDC_CLIENT_ID and OIDC_ISSUER_URL env vars.",
    --     "is_visible": true,
    --     "generated_at": "2026-05-11T10:46:00Z"
    --   },
    --   "developer": {
    --     "body_markdown": "Implement OIDC Authorization Code flow with PKCE. New module: `src/auth/oidc.ts`.",
    --     "is_visible": true,
    --     "generated_at": "2026-05-11T10:46:00Z"
    --   }
    -- }

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_releases_repo_date ON releases(repository_id, release_date DESC);
CREATE INDEX idx_releases_version ON releases USING GIN (version jsonb_path_ops);
-- Enables: WHERE version @> '{"major": 1, "minor": 3}'
CREATE INDEX idx_releases_status ON releases(status);
CREATE INDEX idx_releases_publications ON releases USING GIN (publications);

CREATE INDEX idx_entries_release ON changelog_entries(release_id, display_order);
CREATE INDEX idx_entries_category ON changelog_entries(category);
CREATE INDEX idx_entries_breaking ON changelog_entries(release_id) WHERE is_breaking = TRUE;
CREATE INDEX idx_entries_sources ON changelog_entries USING GIN (sources jsonb_path_ops);
CREATE INDEX idx_entries_audience ON changelog_entries USING GIN (audience_variants);
```

---

## Output Templates & Audit Log

```sql
-- ============================================================
-- TEMPLATES
-- Template body is text; metadata in JSONB
-- ============================================================
CREATE TABLE templates (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id   UUID REFERENCES repositories(id) ON DELETE CASCADE,  -- NULL = built-in
    name            TEXT NOT NULL,
    audience        TEXT,                             -- NULL = universal
    format          TEXT NOT NULL CHECK (format IN ('markdown', 'html', 'json', 'atom', 'rss')),
    template_body   TEXT NOT NULL,
    template_config JSONB NOT NULL DEFAULT '{}',
    -- {
    --   "engine": "tera",
    --   "include_contributors": true,
    --   "include_pr_links": true,
    --   "group_by": "category",
    --   "date_format": "YYYY-MM-DD"
    -- }
    is_default      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- RENDERED CACHE
-- Cached rendered output for each release/audience/format combination
-- ============================================================
CREATE TABLE rendered_cache (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    release_id      UUID NOT NULL REFERENCES releases(id) ON DELETE CASCADE,
    audience        TEXT,                             -- NULL = default/developer
    format          TEXT NOT NULL,
    content         TEXT NOT NULL,
    content_hash    TEXT NOT NULL,                    -- SHA-256 for cache invalidation
    template_id     UUID REFERENCES templates(id),
    rendered_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (release_id, audience, format)
);

-- ============================================================
-- AUDIT LOG
-- Simple append-only audit trail (not event-sourced, but sufficient
-- for compliance and debugging)
-- ============================================================
CREATE TABLE audit_log (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id   UUID REFERENCES repositories(id) ON DELETE SET NULL,
    release_id      UUID REFERENCES releases(id) ON DELETE SET NULL,
    action          TEXT NOT NULL,                    -- 'commit_ingested', 'release_created', 'entry_generated', etc.
    actor           TEXT,                             -- user email, 'ci_pipeline', 'ai_classifier', etc.
    details         JSONB NOT NULL DEFAULT '{}',      -- action-specific details
    -- {
    --   "commit_sha": "abc123",
    --   "classification_type": "feat",
    --   "ai_model": "claude-3.5-sonnet",
    --   "confidence": 0.94
    -- }
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_audit_log_repo ON audit_log(repository_id, occurred_at DESC);
CREATE INDEX idx_audit_log_release ON audit_log(release_id, occurred_at DESC);
CREATE INDEX idx_audit_log_action ON audit_log(action);
CREATE INDEX idx_audit_log_occurred ON audit_log(occurred_at DESC);
CREATE INDEX idx_templates_repository ON templates(repository_id);
CREATE INDEX idx_rendered_cache_release ON rendered_cache(release_id);
```

---

## Table Count Summary

| Category | Tables | Notes |
|----------|--------|-------|
| Repository & Config | 2 | repositories, packages (config in JSONB, no separate tables) |
| Commits | 1 | commits (classification, author, diff stats all in JSONB) |
| Source Items & Links | 2 | source_items (unified PRs/issues/tickets), commit_source_links |
| Releases & Entries | 2 | releases (publications in JSONB), changelog_entries (variants in JSONB) |
| Output | 2 | templates, rendered_cache |
| Audit | 1 | audit_log |
| **Total** | **10** | vs. 23 in the normalized model |

---

## Key Design Decisions

1. **Unified `source_items` table** instead of separate `pull_requests` and `issues` tables — PRs, issues, and tickets are all "source items" that contribute context to changelog entries. The `item_type` column distinguishes them, while provider-specific metadata lives in JSONB. Adding a new provider (e.g., Azure DevOps) requires zero schema changes — just new JSONB shapes.

2. **`classification` JSONB on `commits`** with `previous_classifications` array — stores the current classification alongside its history in a single column. When AI reclassifies a commit, the old classification is pushed into the `previous_classifications` array. This provides audit history without a separate table or event store.

3. **`audience_variants` JSONB on `changelog_entries`** — audience-specific text variants are stored inline rather than in a separate table. This eliminates JOINs for the most common query ("render this release for audience X") and keeps the entry self-contained. The trade-off is that querying across variants (e.g., "all entries visible to admins") uses JSONB operators.

4. **`publications` JSONB array on `releases`** — publication status across multiple channels is stored inline on the release. This avoids a separate junction table for what is fundamentally a small, bounded list (typically 2-5 channels per release). Each publication entry includes its status, timestamp, and provider response.

5. **`commit_source_links` as a relational junction table** despite the JSONB philosophy — this many-to-many relationship is queried in both directions frequently (commits-for-PR and PRs-for-commit), making a proper junction table with indexes more performant than JSONB arrays. The `link_type` field captures how the commit references the source item (fixes, closes, references).

6. **`audit_log` as a simple append-only table** — provides compliance-grade audit trailing without the complexity of full event sourcing. Every significant action is logged with its actor, timestamp, and JSONB details. Sufficient for regulatory requirements without requiring event replay infrastructure.

7. **GIN indexes on all JSONB columns** using `jsonb_path_ops` — enables fast containment queries (`@>` operator) on classification types, version components, source references, and metadata fields. The `jsonb_path_ops` operator class is more compact than the default and supports the most common query patterns.

8. **`version` as JSONB on `releases`** — stores both decomposed fields (major, minor, patch) for programmatic comparison and the raw version string for display. Supports both SemVer and CalVer by including a `scheme` field. The JSONB GIN index enables range queries like "all releases with major version 2".

9. **`generation` JSONB on `changelog_entries`** captures full AI provenance — model used, prompt hash, confidence score, and edit history. The `edit_history` array within the JSONB tracks human edits over time, providing traceability without a separate edits table.

10. **No separate `authors` table** — author information is embedded as JSONB in `commits` and `source_items`. For GDPR erasure, the application layer updates the JSONB to `{"gdpr_erased": true}`. This is simpler than maintaining a normalized authors table with deduplication logic across providers, at the cost of potential data duplication across commits by the same author.

---

## Example Queries

### All features in a release with their Jira context
```sql
SELECT ce.body_markdown,
       ce.sources,
       si.title AS ticket_title,
       si.metadata->>'acceptance_criteria' AS acceptance_criteria
FROM changelog_entries ce,
     jsonb_array_elements_text(ce.sources->'source_item_ids') AS source_id
JOIN source_items si ON si.id = source_id::uuid
WHERE ce.release_id = $1
  AND ce.category = 'Added'
  AND si.provider = 'jira'
ORDER BY ce.display_order;
```

### User-facing release notes for a specific audience
```sql
SELECT ce.category,
       COALESCE(
           ce.audience_variants->'end_user'->>'body_markdown',
           ce.body_markdown
       ) AS entry_text
FROM changelog_entries ce
WHERE ce.release_id = $1
  AND (ce.audience_variants->'end_user'->>'is_visible')::boolean IS DISTINCT FROM FALSE
ORDER BY
    CASE ce.category
        WHEN 'Added' THEN 1
        WHEN 'Changed' THEN 2
        WHEN 'Fixed' THEN 3
        WHEN 'Security' THEN 4
        WHEN 'Deprecated' THEN 5
        WHEN 'Removed' THEN 6
    END,
    ce.display_order;
```

### Find all commits classified as breaking changes
```sql
SELECT c.sha, c.message_subject, c.committed_at,
       c.classification->>'scope' AS scope,
       c.classification->>'user_impact_summary' AS user_impact
FROM commits c
WHERE c.repository_id = $1
  AND c.classification @> '{"is_breaking": true}'
ORDER BY c.committed_at DESC;
```

### Commits with low AI classification confidence (for review)
```sql
SELECT c.sha, c.message_subject,
       c.classification->>'type' AS classified_type,
       (c.classification->>'confidence')::real AS confidence
FROM commits c
WHERE c.repository_id = $1
  AND c.classification IS NOT NULL
  AND (c.classification->>'confidence')::real < 0.7
ORDER BY (c.classification->>'confidence')::real ASC;
```

### Audit trail for a release
```sql
SELECT al.action, al.actor, al.occurred_at,
       al.details
FROM audit_log al
WHERE al.release_id = $1
ORDER BY al.occurred_at;
```
