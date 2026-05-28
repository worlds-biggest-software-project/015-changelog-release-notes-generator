# Data Model Suggestion 1: Entity-Centric Normalized Relational

> Project: Changelog & Release Notes Generator · Created: 2026-05-11

## Philosophy

This model follows traditional normalized relational design where every distinct concept — repositories, commits, pull requests, issues, releases, changelog entries, audience variants — gets its own table with strict foreign key relationships. The schema enforces referential integrity at the database level, ensuring that every changelog entry traces back to a real commit, PR, or issue, and every release belongs to a verified repository.

The approach draws from how GitHub's own API models releases (separate release, asset, and tag objects with explicit relationships) and how Jira structures its version/issue linkages. It prioritizes query flexibility and data integrity over write speed, making it well-suited for a tool that reads git history once and then serves many read queries for different audiences and formats.

Normalized schemas are the standard choice for developer tools with well-defined entity boundaries. The changelog generator's domain is stable — commits, PRs, issues, releases, and entries are well-understood concepts that rarely need schema-on-read flexibility.

**Best for:** Teams that value data integrity, need complex cross-entity queries (e.g., "show all breaking changes across the last 5 releases that originated from Jira epic X"), and want a straightforward schema that maps directly to the domain model.

**Trade-offs:**
- (+) Full referential integrity — orphaned records are impossible
- (+) Standard SQL queries without JSONB operators or event replay
- (+) Easy to reason about, debug, and extend with standard ORM tooling
- (+) Well-suited for complex JOIN queries across entities
- (-) More tables than hybrid approaches (~25 vs. ~15)
- (-) Adding new metadata fields requires migrations
- (-) Provider-specific fields (GitHub vs. GitLab vs. Jira) require either nullable columns or additional junction tables
- (-) No built-in temporal history — current state only (need separate audit mechanism)

---

## Standards Alignment

| Standard | How It's Used |
|----------|---------------|
| Conventional Commits v1.0.0 | `commit_classifications.type` uses the standard type vocabulary (feat, fix, chore, etc.); `commit_classifications.scope` captures the optional scope |
| Semantic Versioning 2.0.0 | `releases.version_major`, `version_minor`, `version_patch`, `version_prerelease` decompose SemVer into queryable components |
| Keep a Changelog v1.1.0 | `changelog_categories` table stores the six canonical categories (Added, Changed, Deprecated, Removed, Fixed, Security) |
| ISO 8601 | All `TIMESTAMPTZ` columns; `releases.release_date` stored as ISO 8601 date |
| CommonMark 0.31.2 | `changelog_entries.body_markdown` and `audience_variants.body_markdown` store CommonMark-compliant content |
| RFC 4287 (Atom) / RSS 2.0 | `distribution_channels` table models feed endpoints for Atom/RSS publication |
| OAuth 2.0 (RFC 6749) | `provider_connections` table stores OAuth tokens for GitHub, GitLab, Jira, Linear |
| GDPR (EU 2016/679) | `authors` table separates PII from commit data; `authors.gdpr_erasure_requested_at` supports right-to-erasure |

---

## Repository & Provider Management

```sql
-- Repositories tracked by the changelog generator
CREATE TABLE repositories (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,                    -- e.g. "my-org/my-repo"
    provider        TEXT NOT NULL CHECK (provider IN ('github', 'gitlab', 'bitbucket', 'local')),
    provider_id     TEXT,                             -- provider-specific repo ID (e.g. GitHub numeric ID)
    default_branch  TEXT NOT NULL DEFAULT 'main',
    clone_url       TEXT,
    api_url         TEXT,                             -- e.g. "https://api.github.com/repos/my-org/my-repo"
    is_monorepo     BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (provider, name)
);

-- Packages within a monorepo (optional; only populated for monorepos)
CREATE TABLE packages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id   UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,                    -- e.g. "@my-org/core"
    path            TEXT NOT NULL,                    -- e.g. "packages/core"
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (repository_id, name)
);

-- OAuth connections to external providers (GitHub, GitLab, Jira, Linear)
CREATE TABLE provider_connections (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id   UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    provider        TEXT NOT NULL CHECK (provider IN ('github', 'gitlab', 'jira', 'linear')),
    access_token    TEXT NOT NULL,                    -- encrypted at rest
    refresh_token   TEXT,                             -- encrypted at rest
    token_expires_at TIMESTAMPTZ,
    api_base_url    TEXT,                             -- e.g. "https://my-company.atlassian.net"
    project_key     TEXT,                             -- e.g. Jira project key "MYAPP"
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (repository_id, provider)
);

CREATE INDEX idx_packages_repository ON packages(repository_id);
CREATE INDEX idx_provider_connections_repository ON provider_connections(repository_id);
```

---

## Author Management (GDPR-Aware)

```sql
-- Authors extracted from commits, PRs, and issues
-- Separated from commits to support GDPR erasure and deduplication
CREATE TABLE authors (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           TEXT,                             -- may be NULL after GDPR erasure
    name            TEXT,                             -- display name; may be NULL after GDPR erasure
    provider        TEXT,                             -- 'github', 'gitlab', etc.
    provider_username TEXT,                           -- e.g. GitHub login
    provider_user_id TEXT,                            -- provider-specific numeric/string ID
    avatar_url      TEXT,
    gdpr_erasure_requested_at TIMESTAMPTZ,            -- set when user requests data deletion
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX idx_authors_email ON authors(email) WHERE email IS NOT NULL;
CREATE UNIQUE INDEX idx_authors_provider ON authors(provider, provider_user_id)
    WHERE provider IS NOT NULL AND provider_user_id IS NOT NULL;
```

---

## Commit & Classification

```sql
-- Raw commits ingested from git history
CREATE TABLE commits (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id   UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    sha             TEXT NOT NULL,
    author_id       UUID REFERENCES authors(id) ON DELETE SET NULL,
    committer_id    UUID REFERENCES authors(id) ON DELETE SET NULL,
    message_subject TEXT NOT NULL,                    -- first line of commit message
    message_body    TEXT,                             -- remaining lines
    committed_at    TIMESTAMPTZ NOT NULL,
    files_changed   INTEGER,
    insertions      INTEGER,
    deletions       INTEGER,
    is_merge_commit BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (repository_id, sha)
);

-- AI or rule-based classification of each commit
CREATE TABLE commit_classifications (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    commit_id       UUID NOT NULL REFERENCES commits(id) ON DELETE CASCADE,
    type            TEXT NOT NULL,                    -- 'feat', 'fix', 'chore', 'docs', 'refactor', 'perf', 'test', 'ci', 'build', 'style', 'breaking'
    scope           TEXT,                             -- e.g. 'parser', 'api', 'ui'
    is_breaking     BOOLEAN NOT NULL DEFAULT FALSE,
    is_internal     BOOLEAN NOT NULL DEFAULT FALSE,   -- true for refactors, chores, CI changes
    confidence      REAL,                             -- 0.0-1.0; NULL if rule-based (certain)
    classification_method TEXT NOT NULL CHECK (classification_method IN ('conventional_commits', 'ai_llm', 'manual', 'label_based')),
    user_impact_summary TEXT,                         -- AI-generated: what this means for users
    developer_summary TEXT,                           -- AI-generated: technical description
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (commit_id)                                -- one classification per commit
);

CREATE INDEX idx_commits_repository_date ON commits(repository_id, committed_at DESC);
CREATE INDEX idx_commits_sha ON commits(sha);
CREATE INDEX idx_classifications_type ON commit_classifications(type);
CREATE INDEX idx_classifications_breaking ON commit_classifications(is_breaking) WHERE is_breaking = TRUE;
```

---

## Pull Requests & Issues

```sql
-- Pull requests / merge requests linked to commits
CREATE TABLE pull_requests (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id   UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    provider_pr_id  TEXT NOT NULL,                    -- e.g. "123" (PR number)
    title           TEXT NOT NULL,
    body            TEXT,                             -- PR description in markdown
    author_id       UUID REFERENCES authors(id) ON DELETE SET NULL,
    state           TEXT NOT NULL CHECK (state IN ('open', 'closed', 'merged')),
    merged_at       TIMESTAMPTZ,
    html_url        TEXT,
    labels          TEXT[],                           -- array of label names
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (repository_id, provider_pr_id)
);

-- Junction: commits belong to pull requests (many-to-many)
CREATE TABLE commit_pull_requests (
    commit_id       UUID NOT NULL REFERENCES commits(id) ON DELETE CASCADE,
    pull_request_id UUID NOT NULL REFERENCES pull_requests(id) ON DELETE CASCADE,
    PRIMARY KEY (commit_id, pull_request_id)
);

-- Issues from issue trackers (GitHub Issues, Jira, Linear)
CREATE TABLE issues (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id   UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    provider        TEXT NOT NULL CHECK (provider IN ('github', 'gitlab', 'jira', 'linear')),
    provider_issue_id TEXT NOT NULL,                  -- e.g. "MYAPP-456" (Jira) or "789" (GitHub)
    title           TEXT NOT NULL,
    body            TEXT,                             -- issue description
    status          TEXT,                             -- 'open', 'closed', 'done', etc.
    issue_type      TEXT,                             -- 'bug', 'story', 'task', 'epic' (Jira types)
    priority        TEXT,                             -- 'critical', 'high', 'medium', 'low'
    labels          TEXT[],
    assignee_id     UUID REFERENCES authors(id) ON DELETE SET NULL,
    html_url        TEXT,
    fix_version     TEXT,                             -- Jira fixVersion field
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (repository_id, provider, provider_issue_id)
);

-- Junction: commits reference issues (many-to-many)
CREATE TABLE commit_issues (
    commit_id       UUID NOT NULL REFERENCES commits(id) ON DELETE CASCADE,
    issue_id        UUID NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
    PRIMARY KEY (commit_id, issue_id)
);

-- Junction: pull requests reference issues (many-to-many)
CREATE TABLE pull_request_issues (
    pull_request_id UUID NOT NULL REFERENCES pull_requests(id) ON DELETE CASCADE,
    issue_id        UUID NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
    PRIMARY KEY (pull_request_id, issue_id)
);

CREATE INDEX idx_pull_requests_repository ON pull_requests(repository_id);
CREATE INDEX idx_pull_requests_merged ON pull_requests(merged_at DESC) WHERE state = 'merged';
CREATE INDEX idx_issues_repository_provider ON issues(repository_id, provider);
CREATE INDEX idx_issues_fix_version ON issues(fix_version) WHERE fix_version IS NOT NULL;
```

---

## Releases & Changelog Entries

```sql
-- Changelog category definitions (Keep a Changelog v1.1.0 canonical + custom)
CREATE TABLE changelog_categories (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id   UUID REFERENCES repositories(id) ON DELETE CASCADE,  -- NULL = global default
    name            TEXT NOT NULL,                    -- 'Added', 'Changed', 'Deprecated', 'Removed', 'Fixed', 'Security'
    display_order   INTEGER NOT NULL DEFAULT 0,
    commit_types    TEXT[],                           -- which commit types map here, e.g. {'feat'} -> 'Added'
    icon            TEXT,                             -- optional emoji: '🚀', '🐛', etc.
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Releases (versions) for a repository or package
CREATE TABLE releases (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id   UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    package_id      UUID REFERENCES packages(id) ON DELETE CASCADE,  -- NULL for single-package repos
    tag_name        TEXT NOT NULL,                    -- e.g. "v1.2.3"
    version_major   INTEGER NOT NULL,
    version_minor   INTEGER NOT NULL,
    version_patch   INTEGER NOT NULL,
    version_prerelease TEXT,                          -- e.g. "alpha.1", "beta.2"
    version_build_metadata TEXT,                      -- e.g. "build.123"
    version_scheme  TEXT NOT NULL DEFAULT 'semver' CHECK (version_scheme IN ('semver', 'calver', 'custom')),
    release_date    DATE NOT NULL,                    -- ISO 8601 date
    title           TEXT,                             -- optional human-readable title
    is_draft        BOOLEAN NOT NULL DEFAULT FALSE,
    is_prerelease   BOOLEAN NOT NULL DEFAULT FALSE,
    is_yanked       BOOLEAN NOT NULL DEFAULT FALSE,   -- Keep a Changelog [YANKED] marker
    previous_release_id UUID REFERENCES releases(id), -- link to prior release for diffing
    from_commit_sha TEXT,                             -- start of commit range (exclusive)
    to_commit_sha   TEXT NOT NULL,                    -- end of commit range (inclusive, usually the tag)
    provider_release_id TEXT,                         -- GitHub/GitLab release ID if published
    provider_release_url TEXT,                        -- URL to the published release
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (repository_id, tag_name)
);

-- Individual changelog entries within a release
CREATE TABLE changelog_entries (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    release_id      UUID NOT NULL REFERENCES releases(id) ON DELETE CASCADE,
    category_id     UUID NOT NULL REFERENCES changelog_categories(id),
    body_markdown   TEXT NOT NULL,                    -- CommonMark content
    display_order   INTEGER NOT NULL DEFAULT 0,
    is_breaking     BOOLEAN NOT NULL DEFAULT FALSE,
    is_security     BOOLEAN NOT NULL DEFAULT FALSE,
    is_highlight    BOOLEAN NOT NULL DEFAULT FALSE,   -- flagged as notable for summaries
    generation_method TEXT NOT NULL CHECK (generation_method IN ('ai_generated', 'manual', 'template_based')),
    ai_model_used   TEXT,                             -- e.g. "claude-3.5-sonnet" if AI-generated
    ai_prompt_hash  TEXT,                             -- hash of the prompt used, for reproducibility
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Junction: changelog entries trace back to specific commits
CREATE TABLE entry_commits (
    entry_id        UUID NOT NULL REFERENCES changelog_entries(id) ON DELETE CASCADE,
    commit_id       UUID NOT NULL REFERENCES commits(id) ON DELETE CASCADE,
    PRIMARY KEY (entry_id, commit_id)
);

-- Junction: changelog entries trace back to specific PRs
CREATE TABLE entry_pull_requests (
    entry_id        UUID NOT NULL REFERENCES changelog_entries(id) ON DELETE CASCADE,
    pull_request_id UUID NOT NULL REFERENCES pull_requests(id) ON DELETE CASCADE,
    PRIMARY KEY (entry_id, pull_request_id)
);

-- Junction: changelog entries trace back to specific issues
CREATE TABLE entry_issues (
    entry_id        UUID NOT NULL REFERENCES changelog_entries(id) ON DELETE CASCADE,
    issue_id        UUID NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
    PRIMARY KEY (entry_id, issue_id)
);

CREATE INDEX idx_releases_repository_date ON releases(repository_id, release_date DESC);
CREATE INDEX idx_releases_version ON releases(repository_id, version_major DESC, version_minor DESC, version_patch DESC);
CREATE INDEX idx_changelog_entries_release ON changelog_entries(release_id, display_order);
CREATE INDEX idx_changelog_entries_breaking ON changelog_entries(release_id) WHERE is_breaking = TRUE;
```

---

## Audience Variants

```sql
-- Audience definitions (developer, end-user, admin, etc.)
CREATE TABLE audiences (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL UNIQUE,             -- 'developer', 'end_user', 'admin', 'security'
    description     TEXT,
    display_order   INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Audience-specific variant of a changelog entry
-- Each entry can have different wording for different audiences
CREATE TABLE audience_variants (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entry_id        UUID NOT NULL REFERENCES changelog_entries(id) ON DELETE CASCADE,
    audience_id     UUID NOT NULL REFERENCES audiences(id) ON DELETE CASCADE,
    body_markdown   TEXT NOT NULL,                    -- audience-tailored CommonMark content
    is_visible      BOOLEAN NOT NULL DEFAULT TRUE,    -- false = this entry is filtered out for this audience
    generation_method TEXT NOT NULL CHECK (generation_method IN ('ai_generated', 'manual', 'template_based')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (entry_id, audience_id)
);

CREATE INDEX idx_audience_variants_entry ON audience_variants(entry_id);
CREATE INDEX idx_audience_variants_audience ON audience_variants(audience_id);
```

---

## Output & Distribution

```sql
-- Rendered changelog documents (cached output)
CREATE TABLE rendered_changelogs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    release_id      UUID NOT NULL REFERENCES releases(id) ON DELETE CASCADE,
    audience_id     UUID REFERENCES audiences(id),    -- NULL = universal/developer default
    format          TEXT NOT NULL CHECK (format IN ('markdown', 'html', 'json', 'atom', 'rss', 'plaintext')),
    content         TEXT NOT NULL,                    -- the rendered document
    content_hash    TEXT NOT NULL,                    -- SHA-256 of content for cache invalidation
    template_name   TEXT,                             -- which template was used
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (release_id, audience_id, format)
);

-- Distribution channels for publishing release notes
CREATE TABLE distribution_channels (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id   UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    channel_type    TEXT NOT NULL CHECK (channel_type IN ('github_release', 'gitlab_release', 'changelog_file', 'atom_feed', 'rss_feed', 'slack', 'email', 'webhook')),
    audience_id     UUID REFERENCES audiences(id),    -- which audience variant to publish
    config          JSONB NOT NULL DEFAULT '{}',       -- channel-specific configuration
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- config example for 'slack':
-- {"webhook_url": "https://hooks.slack.com/...", "channel": "#releases"}
-- config example for 'changelog_file':
-- {"file_path": "CHANGELOG.md", "branch": "main", "auto_commit": true}

-- Publication log: track when and where each release was published
CREATE TABLE publications (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    release_id      UUID NOT NULL REFERENCES releases(id) ON DELETE CASCADE,
    channel_id      UUID NOT NULL REFERENCES distribution_channels(id) ON DELETE CASCADE,
    status          TEXT NOT NULL CHECK (status IN ('pending', 'published', 'failed')),
    published_at    TIMESTAMPTZ,
    error_message   TEXT,
    provider_response JSONB,                          -- raw response from the provider API
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (release_id, channel_id)
);

CREATE INDEX idx_rendered_changelogs_release ON rendered_changelogs(release_id);
CREATE INDEX idx_distribution_channels_repository ON distribution_channels(repository_id);
CREATE INDEX idx_publications_release ON publications(release_id);
CREATE INDEX idx_publications_status ON publications(status) WHERE status = 'pending';
```

---

## Configuration & Templates

```sql
-- Per-repository configuration for the changelog generator
CREATE TABLE repository_configs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id   UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE UNIQUE,
    llm_provider    TEXT DEFAULT 'anthropic',         -- 'anthropic', 'openai', 'ollama'
    llm_model       TEXT DEFAULT 'claude-3.5-sonnet',
    commit_filter_patterns TEXT[],                    -- regex patterns to exclude (e.g. '^Merge', '^chore\(deps\)')
    include_contributor_acknowledgement BOOLEAN DEFAULT TRUE,
    include_pr_links BOOLEAN DEFAULT TRUE,
    include_issue_links BOOLEAN DEFAULT TRUE,
    version_scheme  TEXT NOT NULL DEFAULT 'semver' CHECK (version_scheme IN ('semver', 'calver', 'custom')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Output templates (Tera/Handlebars/Jinja2)
CREATE TABLE templates (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id   UUID REFERENCES repositories(id) ON DELETE CASCADE,  -- NULL = built-in default
    name            TEXT NOT NULL,
    audience_id     UUID REFERENCES audiences(id),    -- NULL = universal
    format          TEXT NOT NULL CHECK (format IN ('markdown', 'html', 'json', 'atom', 'rss')),
    template_body   TEXT NOT NULL,                    -- template source code
    is_default      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_templates_repository ON templates(repository_id);
```

---

## Table Count Summary

| Category | Tables | Notes |
|----------|--------|-------|
| Repository & Provider | 3 | repositories, packages, provider_connections |
| Authors | 1 | GDPR-aware author records |
| Commits & Classification | 2 | commits, commit_classifications |
| Pull Requests & Issues | 5 | pull_requests, issues, + 3 junction tables |
| Releases & Entries | 5 | releases, changelog_categories, changelog_entries, + 3 entry junction tables (traceability) |
| Audience Variants | 2 | audiences, audience_variants |
| Output & Distribution | 3 | rendered_changelogs, distribution_channels, publications |
| Configuration | 2 | repository_configs, templates |
| **Total** | **23** | |

---

## Key Design Decisions

1. **Separate `commit_classifications` table** rather than columns on `commits` — allows re-classification (e.g., switching from rule-based to AI) without losing the original commit data. The classification is the tool's opinion; the commit is a fact.

2. **Three entry junction tables (`entry_commits`, `entry_pull_requests`, `entry_issues`)** provide full bidirectional traceability from any changelog entry back to its source commits, PRs, and issues. This satisfies the compliance audit trail requirement identified in the features survey.

3. **Decomposed SemVer fields** (`version_major`, `version_minor`, `version_patch`) on `releases` instead of a single `version` string — enables efficient version-range queries (e.g., "all releases between 2.0.0 and 3.0.0") using standard integer comparison rather than string parsing.

4. **GDPR-aware `authors` table** with an explicit `gdpr_erasure_requested_at` field — when set, the application layer NULLs out `email` and `name` while preserving the author ID for referential integrity. Commit data remains intact but is de-identified.

5. **`audiences` + `audience_variants` pattern** decouples audience definitions from entry content — a single changelog entry gets multiple body texts, one per audience, with visibility control. This directly addresses the "developer-to-user translation gap" identified as the top unserved opportunity.

6. **`rendered_changelogs` as a cache table** with `content_hash` — avoids re-rendering on every read. When entries or variants change, the hash invalidates and the document is re-rendered on next access.

7. **`distribution_channels` with JSONB `config`** — the one intentional denormalization in this model. Channel-specific configuration (Slack webhook URLs, file paths, email lists) varies too much between channel types to normalize into separate tables without excessive complexity.

8. **`classification_method` and `generation_method` fields** record provenance — whether content was produced by Conventional Commits parsing, AI/LLM, or manual authoring. Essential for trust, debugging, and improving AI quality over time.

9. **Monorepo support via `packages` table** with optional `package_id` on `releases` — single-package repositories simply leave `package_id` NULL. No schema overhead for the common case.

10. **`previous_release_id` self-reference on `releases`** enables efficient "what changed since last release" queries without scanning the full release history.

---

## Example Queries

### All breaking changes in a release with their source commits
```sql
SELECT ce.body_markdown, c.sha, c.message_subject
FROM changelog_entries ce
JOIN entry_commits ec ON ec.entry_id = ce.id
JOIN commits c ON c.id = ec.commit_id
WHERE ce.release_id = $1
  AND ce.is_breaking = TRUE
ORDER BY ce.display_order;
```

### User-facing release notes for a specific release
```sql
SELECT cc.name AS category,
       COALESCE(av.body_markdown, ce.body_markdown) AS entry_text
FROM changelog_entries ce
JOIN changelog_categories cc ON cc.id = ce.category_id
LEFT JOIN audience_variants av ON av.entry_id = ce.id
    AND av.audience_id = (SELECT id FROM audiences WHERE name = 'end_user')
    AND av.is_visible = TRUE
WHERE ce.release_id = $1
ORDER BY cc.display_order, ce.display_order;
```

### Commits not yet included in any release
```sql
SELECT c.sha, c.message_subject, c.committed_at, cc.type
FROM commits c
LEFT JOIN commit_classifications cc ON cc.commit_id = c.id
WHERE c.repository_id = $1
  AND c.committed_at > (
      SELECT MAX(r.release_date) FROM releases r WHERE r.repository_id = $1
  )
ORDER BY c.committed_at DESC;
```
