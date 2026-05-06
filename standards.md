# Standards & API Reference

> Project: Changelog & Release Notes Generator · Generated: 2026-05-04

---

## Industry Standards & Specifications

### Versioning & Release Conventions

**Semantic Versioning 2.0.0 (SemVer)**
- URL: https://semver.org/
- Specification authored by Tom Preston-Werner (GitHub co-founder). Defines the MAJOR.MINOR.PATCH version format with strict rules: PATCH for backwards-compatible bug fixes, MINOR for backwards-compatible new features, MAJOR for breaking changes. The changelog generator must understand SemVer to calculate the correct next version from commit history. The official GitHub repository is at https://github.com/semver/semver.

**Conventional Commits 1.0.0**
- URL: https://www.conventionalcommits.org/en/v1.0.0/
- A lightweight specification for structuring commit messages as `<type>[optional scope]: <description>` with optional body and footer. Maps directly to SemVer: `fix:` → PATCH, `feat:` → MINOR, `BREAKING CHANGE:` footer or `!` suffix → MAJOR. This is the primary input format that changelog generators parse. Licensed under CC BY 3.0. Tooling ecosystem listed at https://www.conventionalcommits.org/en/about/.

**Keep a Changelog 1.1.0**
- URL: https://keepachangelog.com/en/1.1.0/
- Human-oriented format specification for CHANGELOG.md files. Defines six change categories (Added, Changed, Deprecated, Removed, Fixed, Security), an Unreleased section at the top, newest versions first, ISO 8601 dates (YYYY-MM-DD), and SemVer version headings. The definitive reference for structured, human-readable output. GitHub source: https://github.com/olivierlacan/keep-a-changelog.

**ISO 8601-1:2019 — Date and Time Representations**
- URL: https://www.iso.org/standard/70907.html
- The international standard for date and time interchange. Defines the YYYY-MM-DD format used universally in changelogs and release notes (including by the Keep a Changelog spec). Adopted by RFC 3339 (https://datatracker.ietf.org/doc/html/rfc3339) for internet timestamps. Ensures that release dates in changelogs sort correctly both lexicographically and chronologically.

**Software Versioning — Calendar Versioning (CalVer)**
- URL: https://calver.org/
- An alternative to SemVer that uses dates as version components (e.g., `2026.05.04`). Used by Ubuntu, pip, and other projects. A changelog generator should support CalVer projects in addition to SemVer ones.

---

### Data Format Standards

**OpenAPI Specification 3.1 / 3.2**
- URL: https://spec.openapis.org/oas/v3.2.0.html and https://swagger.io/specification/
- Machine-readable interface definition for REST APIs. Version 3.1+ achieves full JSON Schema 2020-12 compliance. Relevant for defining the changelog generator's own REST API surface and for consuming the GitHub, GitLab, and Jira APIs (which expose OpenAPI specs). Maintained by the OpenAPI Initiative under the Linux Foundation. The OAI GitHub repository is at https://github.com/OAI/OpenAPI-Specification.

**JSON Schema Draft 2020-12**
- URL: https://json-schema.org/specification
- The standard for validating and describing JSON data structures. Used by OpenAPI 3.1, by tool configurations (Changesets `.changeset/config.json`, semantic-release `.releaserc`), and for defining release manifest schemas. Enables machine-readable validation of configuration files and API request/response payloads.

**RFC 4180 — CSV Format**
- URL: https://datatracker.ietf.org/doc/html/rfc4180
- Defines the common format for comma-separated value files. Relevant if the changelog generator needs to export issue or commit data in tabular form for downstream consumption by reporting or audit tools.

**Markdown (CommonMark 0.31.2)**
- URL: https://spec.commonmark.org/
- The de facto standard for changelog and release note content. All major changelog tools (Keep a Changelog, towncrier, git-cliff, Release Drafter) produce CommonMark-compatible Markdown. The changelog generator's output should conform to CommonMark to ensure portability across renderers (GitHub, GitLab, npm, PyPI, etc.).

---

### Feed & Distribution Standards

**RFC 4287 — The Atom Syndication Format**
- URL: https://datatracker.ietf.org/doc/html/rfc4287
- IETF Proposed Standard (December 2005) for an XML-based feed format. Defines the `<feed>` and `<entry>` elements with registered MIME type `application/atom+xml`. A changelog generator can publish release notes as an Atom feed (each release as an `<entry>`) to enable subscription-based changelog delivery. Related: RFC 5005 (Feed Paging and Archiving) at https://datatracker.ietf.org/doc/html/rfc5005.

**RSS 2.0**
- URL: https://www.rssboard.org/rss-specification
- The older, widely adopted feed format with 62% syndication adoption (vs. Atom's wider use in real-time aggregation). Many CI/CD and release monitoring tools support RSS. A changelog generator may expose releases as an RSS feed for compatibility with existing tooling and consumer workflows.

---

### Security & Authentication Standards

**RFC 6749 — The OAuth 2.0 Authorization Framework**
- URL: https://datatracker.ietf.org/doc/html/rfc6749
- The foundational standard for delegated authorisation. Defines four grant types; the Authorization Code grant (with PKCE per RFC 7636) is required for connecting to GitHub, GitLab, Jira, and Linear on behalf of users. All major VCS and issue-tracking platforms implement OAuth 2.0 for third-party app access. Essential for the changelog generator's authentication layer.

**OpenID Connect Core 1.0**
- URL: https://openid.net/specs/openid-connect-core-1_0.html
- An identity layer on top of OAuth 2.0 (published February 2014 by the OpenID Foundation). Enables the changelog generator to verify user identity (not just obtain access tokens) when integrating with platforms that support OIDC (GitHub Actions, GitLab, enterprise Jira). The November 2025 MCP specification update added OIDC Discovery 1.0 alignment for authorization servers.

**GDPR (EU Regulation 2016/679)**
- URL: https://eur-lex.europa.eu/eli/reg/2016/679/oj
- EU data protection regulation directly relevant because git commit history contains personal data (author names, email addresses). The changelog generator must implement data minimisation (only display necessary author information), support erasure requests, and avoid storing personal data beyond what is required. Non-compliance risks fines up to €20M or 4% of global turnover.

**OWASP API Security Top 10**
- URL: https://owasp.org/www-project-api-security/
- Industry reference for API security risks. Of particular relevance: Broken Object Level Authorisation (BOLA) when fetching repository/issue data across organisations, and Broken Authentication when handling OAuth tokens and API keys. The changelog generator's API integration code should be audited against this list.

---

### MCP Server Specifications

**Model Context Protocol (MCP) — November 2025 Specification**
- URL: https://modelcontextprotocol.io/specification/2025-11-25/changelog
- GitHub: https://github.com/modelcontextprotocol/modelcontextprotocol
- The open protocol (Anthropic, November 2024; v2 November 2025) for structured AI-tool integration. The November 2025 release added tool icons, concurrent tool execution, input validation error handling as Tool Execution Errors, and OIDC Discovery alignment. A changelog generator exposed as an MCP server would allow AI assistants (Claude, Cursor, etc.) to query commit history, generate release notes, and draft changelogs directly through natural-language prompts. The MCP servers repository at https://github.com/modelcontextprotocol/servers provides reference implementations.

**ISO/IEC/IEEE 15289:2019 — Software Lifecycle Documentation**
- URL: https://www.iso.org/standard/74909.html
- Specifies the purpose and content of systems and software life-cycle information items. Defines generic document types (description, plan, report, specification) that map to release notes artefacts. Relevant when the changelog generator must produce formally structured release documentation for regulated industries (aerospace, medical devices, defence).

**ISO/IEC/IEEE 26514:2022 — Design and Development of Information for Users**
- URL: https://www.iso.org/standard/77451.html
- Provides requirements for the structure, content, and format of user-facing software documentation. Applies to changelog and release notes as user documentation artefacts. Recommends that documentation development occur in parallel with software development — a principle embodied by automated changelog generation from commit history.

---

## Similar Products — Developer Documentation & APIs

### GitHub Releases

- **Description:** GitHub's built-in release management system, tightly coupled with Git tags. Supports draft and pre-releases, auto-generated release notes from merged pull requests, and asset attachment. The `generate-notes` endpoint creates AI-assisted release notes from PR titles and labels without requiring Conventional Commits.
- **API Documentation:** https://docs.github.com/en/rest/releases/releases
- **GraphQL API:** https://docs.github.com/en/graphql
- **SDKs/Libraries:**
  - Octokit (JavaScript/TypeScript): https://github.com/octokit/octokit.js — the official GitHub SDK
  - `@octokit/auth-token` for token auth: https://github.com/octokit/auth-token.js
  - PyGitHub (Python): https://github.com/PyGithub/PyGithub
  - Go: https://github.com/google/go-github
- **Developer Guide:** https://docs.github.com/en/rest/about-the-rest-api/about-the-rest-api
- **Standards:** REST/JSON, GraphQL, OpenAPI 3.x
- **Authentication:** OAuth 2.0, Personal Access Tokens (`ghp_*`), GitHub Apps (installation tokens `ghs_*`), GITHUB_TOKEN in Actions; `Authorization: Bearer <token>` header; API version header `X-GitHub-Api-Version: 2026-03-10`

**Key REST Endpoints:**
| Operation | Method | Path |
|-----------|--------|------|
| List releases | GET | `/repos/{owner}/{repo}/releases` |
| Create release | POST | `/repos/{owner}/{repo}/releases` |
| Generate release notes | POST | `/repos/{owner}/{repo}/releases/generate-notes` |
| Get latest release | GET | `/repos/{owner}/{repo}/releases/latest` |
| Get release by tag | GET | `/repos/{owner}/{repo}/releases/tags/{tag}` |
| Update release | PATCH | `/repos/{owner}/{repo}/releases/{release_id}` |
| Delete release | DELETE | `/repos/{owner}/{repo}/releases/{release_id}` |

---

### GitLab Releases

- **Description:** GitLab CE/EE release management integrated with tags, milestones, and CI/CD pipelines. Supports upcoming/historical releases, evidence collection (Premium/Ultimate), asset links, and Markdown descriptions. Available on GitLab.com and self-hosted instances.
- **API Documentation:** https://docs.gitlab.com/api/releases/
- **REST Auth Documentation:** https://docs.gitlab.com/api/rest/authentication/
- **SDKs/Libraries:**
  - python-gitlab: https://python-gitlab.readthedocs.io/
  - node-gitlab: https://jdalrymple.github.io/gitbeaker/
  - Go: https://github.com/xanzy/go-gitlab
- **Developer Guide:** https://docs.gitlab.com/user/project/releases/
- **Standards:** REST/JSON; GitLab exposes a partial OpenAPI schema
- **Authentication:** Personal Access Tokens (`PRIVATE-TOKEN` header), CI/CD Job Tokens (`JOB-TOKEN` header), OAuth 2.0 access tokens (`Authorization: Bearer`); Developer role required to create, Maintainer role to delete

**Key REST Endpoints:**
| Operation | Method | Path |
|-----------|--------|------|
| List releases | GET | `/projects/:id/releases` |
| Get release by tag | GET | `/projects/:id/releases/:tag_name` |
| Latest release | GET | `/projects/:id/releases/permalink/latest` |
| Create release | POST | `/projects/:id/releases` |
| Update release | PUT | `/projects/:id/releases/:tag_name` |
| Delete release | DELETE | `/projects/:id/releases/:tag_name` |
| Collect evidence | POST | `/projects/:id/releases/:tag_name/evidence` |

---

### Jira (Atlassian)

- **Description:** The industry-standard issue tracker. Jira's `fixVersion` field links issues to releases, and JQL (Jira Query Language) enables querying all issues resolved in a given version. The `/rest/api/3/project/{projectIdOrKey}/versions` endpoint exposes version data for automated release note compilation. Note: Atlassian V2 Marketplace APIs are deprecated as of June 30, 2026 — use V3 endpoints.
- **API Documentation:** https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/
- **Project Versions Endpoint:** https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-versions/
- **Developer Changelog:** https://developer.atlassian.com/cloud/jira/platform/changelog/
- **SDKs/Libraries:**
  - Python (`jira`): https://jira.readthedocs.io/
  - JavaScript (`jira.js`): https://mrrefactoring.github.io/jira.js/
  - Java Atlassian REST Client: https://bitbucket.org/atlassian/jira-rest-java-client
- **Developer Guide:** https://developer.atlassian.com/cloud/jira/platform/
- **Standards:** REST/JSON, OpenAPI 3.x (Jira Cloud REST API is now documented in OpenAPI format)
- **Authentication:** OAuth 2.0 (3LO) for user-context access (https://developer.atlassian.com/cloud/jira/platform/oauth-2-3lo-apps/), API tokens with Basic Auth (email + token) for server-side scripts; `Authorization: Basic base64(email:token)` header

---

### Linear

- **Description:** Modern issue tracking platform popular with engineering teams. Provides a fully public GraphQL API (the same API Linear uses internally) covering issues, projects, cycles, and teams. Relevant for generating changelogs from Linear issues linked to a release or cycle.
- **API Documentation:** https://developers.linear.app/docs
- **GraphQL Getting Started:** https://linear.app/developers/graphql
- **GraphQL Endpoint:** `https://api.linear.app/graphql`
- **Schema Explorer:** https://studio.apollographql.com/public/Linear-API/schema/reference
- **SDKs/Libraries:**
  - TypeScript/JavaScript (`@linear/sdk`): https://www.npmjs.com/package/@linear/sdk — strongly typed, code-generated from the GraphQL schema; Node.js 18+ required
  - GitHub (mono-repo): https://github.com/linear/linear
- **Developer Guide:** https://developers.linear.app/docs/graphql/working-with-the-graphql-api
- **Webhooks:** https://linear.app/developers/sdk-webhooks
- **Standards:** GraphQL
- **Authentication:** Personal API keys or OAuth 2.0; `Authorization: <token>` header. Rate limits: 1,500 req/hr (API key), 500 req/hr per user/app (OAuth)

---

### semantic-release

- **Description:** Fully automated npm package release workflow. Analyzes commit messages (Angular convention / Conventional Commits by default), determines the next SemVer version, generates release notes, publishes to npm, and creates a GitHub/GitLab release — all without human intervention. Executes nine sequential steps: Verify Conditions → Get Last Release → Analyze Commits → Verify Release → Generate Notes → Create Git Tag → Prepare → Publish → Notify.
- **API Documentation / Plugin API:** https://semantic-release.gitbook.io/semantic-release/
- **Configuration Reference:** https://semantic-release.gitbook.io/semantic-release/usage/configuration
- **Plugin List:** https://semantic-release.gitbook.io/semantic-release/extending/plugins-list
- **GitHub Actions Recipe:** https://semantic-release.gitbook.io/semantic-release/recipes/ci-configurations/github-actions
- **NPM Package:** https://www.npmjs.com/package/semantic-release
- **SDKs/Libraries:**
  - Core plugins (bundled): `@semantic-release/commit-analyzer`, `@semantic-release/release-notes-generator`, `@semantic-release/npm`, `@semantic-release/github`
  - Additional: `@semantic-release/changelog` (https://github.com/semantic-release/changelog), `@semantic-release/git`
  - Commit analyzer: https://github.com/semantic-release/commit-analyzer
  - Release notes generator: https://github.com/semantic-release/release-notes-generator
- **Developer Guide:** https://semantic-release.gitbook.io/semantic-release/usage/installation
- **Standards:** Conventional Commits, SemVer, CommonMark
- **Authentication:** `GITHUB_TOKEN` or `GITLAB_TOKEN` environment variable; npm `NPM_TOKEN`; OIDC-based trusted publishing supported via GitHub Actions

**Configuration Format:** `.releaserc` (YAML or JSON) or `release.config.js/cjs/mjs`; plugins defined as ordered arrays; options cannot be set via CLI — must be in config file.

---

### conventional-changelog

- **Description:** The npm ecosystem of tools for generating changelogs from Conventional Commits history. The monorepo ships a collection of composable packages: a core pipeline library, a CLI, parsers, writers, and format-specific presets (Angular, Ember, ESLint, jQuery, etc.). Higher-level tools like `commit-and-tag-version` and `semantic-release` build on top of it.
- **API Documentation:** https://github.com/conventional-changelog/conventional-changelog
- **Core Package (npm):** https://www.npmjs.com/package/conventional-changelog-core
- **CLI Package (npm):** https://www.npmjs.com/package/conventional-changelog-cli
- **SDKs/Libraries (key packages):**
  - `conventional-changelog` — CLI entry point: https://www.npmjs.com/package/conventional-changelog
  - `conventional-changelog-core` — programmatic API (returns a readable stream): https://www.npmjs.com/package/conventional-changelog-core
  - `conventional-commits-parser` — parses raw commit strings: https://www.npmjs.com/package/conventional-commits-parser
  - `conventional-changelog-writer` — Handlebars-based changelog renderer
  - `conventional-recommended-bump` — determines SemVer bump type
  - `@conventional-changelog/git-client` — git integration layer
- **Developer Guide:** https://github.com/conventional-changelog/conventional-changelog/tree/master/packages/conventional-changelog-core
- **Standards:** Conventional Commits, SemVer, CommonMark; TypeScript (74%) / JavaScript (26%) codebase; ISC License
- **Authentication:** N/A — operates on local git history; does not connect to external APIs directly

**Monorepo support:** Supports lerna-style monorepos with `foo-package@1.0.0` tag format via `packagePrefix` utility. Managed as a pnpm workspace.

---

### Release Drafter

- **Description:** GitHub Actions app (formerly a Probot app) that automatically drafts the next release as pull requests are merged. It categorises PRs by label, resolves the next SemVer version from label-based rules, and writes a draft release body using a configurable Handlebars-style template. Configuration supports shared organisation-wide files via Probot Config.
- **API Documentation / Repository:** https://github.com/release-drafter/release-drafter
- **GitHub Marketplace:** https://github.com/marketplace/actions/release-drafter
- **SDKs/Libraries:** None (pure GitHub Actions YAML workflow); uses `secrets.GITHUB_TOKEN`
- **Developer Guide:** https://github.com/release-drafter/release-drafter (README is the primary reference)
- **Standards:** GitHub Actions workflow YAML, CommonMark; configuration in `.github/release-drafter.yml`
- **Authentication:** `secrets.GITHUB_TOKEN` (default); custom token via `token` input; required permissions: `contents: write`, `pull-requests: read`

**Configuration Schema (`.github/release-drafter.yml`):**
```yaml
name-template: 'v$RESOLVED_VERSION'
tag-template:  'v$RESOLVED_VERSION'
categories:
  - title: '🚀 Features'
    labels: ['feature', 'enhancement']
  - title: '🐛 Bug Fixes'
    label: 'fix'
version-resolver:
  major: { labels: ['major'] }
  minor: { labels: ['minor', 'feature'] }
  patch: { labels: ['patch', 'fix', 'bugfix'] }
change-template: '- $TITLE @$AUTHOR (#$NUMBER)'
template: |
  ## Changes
  $CHANGES
```

---

### Changesets

- **Description:** Monorepo-first versioning and changelog tool. Developers add markdown "changeset" files (stored in `.changeset/`) describing their changes and semver bump intent as they work. When releasing, the CLI consolidates all changeset files, bumps versions, updates inter-package dependencies, and writes changelogs — then deletes the changeset files. Used by Chakra UI, SvelteKit, Astro, Apollo Client, and Remix.
- **API Documentation / Repository:** https://github.com/changesets/changesets
- **Documentation Site:** https://changesets-docs.vercel.app/
- **Config File Options:** https://github.com/changesets/changesets/blob/main/docs/config-file-options.md
- **GitHub Action:** https://github.com/changesets/action
- **SDKs/Libraries:**
  - `@changesets/cli` — primary CLI tool
  - `@changesets/changelog-git` — changelog generator using git metadata
  - Vercel Academy guide: https://vercel.com/academy/production-monorepos/changesets-versioning
- **Developer Guide:** https://github.com/changesets/changesets/blob/main/docs/intro-to-using-changesets.md
- **Standards:** CommonMark (changeset files are Markdown with YAML front matter), SemVer, JSON Schema (`.changeset/config.json`)
- **Authentication:** N/A for CLI; GitHub Action uses `GITHUB_TOKEN`; supports npm publish with `NPM_TOKEN`

**Changeset file format:**
```markdown
---
"@my-org/package-a": minor
"@my-org/package-b": patch
---

Add new export `fooBar` to package-a and fix null handling in package-b.
```

**Configuration (`.changeset/config.json`):**
```json
{
  "$schema": "https://unpkg.com/@changesets/config/schema.json",
  "changelog": "@changesets/changelog-git",
  "commit": false,
  "linked": [],
  "access": "public",
  "baseBranch": "main",
  "updateInternalDependencies": "patch"
}
```

---

### towncrier

- **Description:** Python-ecosystem changelog tool used by Twisted, pytest, pip, attrs, and BuildBot. Instead of parsing git history, it reads discrete "news fragment" files written by developers and contributors at the time of the change. Produces reStructuredText or Markdown changelogs by assembling fragments by type. Keeps contributor-authored prose separate from raw commit noise.
- **API Documentation:** https://towncrier.readthedocs.io/en/stable/
- **Tutorial:** https://towncrier.readthedocs.io/en/stable/tutorial.html
- **Markdown Guide:** https://towncrier.readthedocs.io/en/stable/markdown.html
- **PyPI:** https://pypi.org/project/towncrier/
- **GitHub:** https://github.com/twisted/towncrier
- **SDKs/Libraries:** Pure Python CLI; no SDK. Current version: 25.8.0. Installable via `pip install towncrier`.
- **Developer Guide:** https://towncrier.readthedocs.io/en/stable/
- **Standards:** reStructuredText (default) or CommonMark output; configuration via `[tool.towncrier]` in `pyproject.toml` (PEP 518) or `towncrier.toml`
- **Authentication:** N/A — operates on local filesystem fragment files only

**Fragment naming convention:** `{issue_number}.{type}.rst` (or `.md`). For orphan fragments (no issue): `+description.type.rst`.

**Built-in fragment types:** `bugfix`, `doc`, `removal`, `misc` (plus configurable custom types).

**Key CLI commands:**
```bash
towncrier build    # assemble changelog from fragments
towncrier create   # create a new fragment
towncrier check    # verify fragments exist for current branch
```

---

### git-cliff

- **Description:** Highly customisable changelog generator written in Rust. Parses Conventional Commits by default but supports arbitrary commit formats via regex. Uses a Tera (Jinja2-inspired) template engine for output formatting, can fetch PR/issue metadata from GitHub/GitLab/Gitea/Bitbucket, and integrates into CI/CD via a dedicated GitHub Action. Current version: v2.13.0.
- **API Documentation:** https://git-cliff.org/docs/
- **Configuration Reference:** https://git-cliff.org/docs/configuration/
- **GitHub Integration:** https://git-cliff.org/docs/integration/github/
- **GitHub Actions Docs:** https://git-cliff.org/docs/category/github-actions/
- **crates.io:** https://crates.io/crates/git-cliff
- **GitHub:** https://github.com/orhun/git-cliff
- **SDKs/Libraries:**
  - `git-cliff-action` (GitHub Action): https://github.com/orhun/git-cliff-action — available on the GitHub Marketplace at https://github.com/marketplace/actions/git-cliff-changelog-generator
  - npm package wrapper also available for JavaScript projects
- **Developer Guide:** https://git-cliff.org/docs/ (Getting Started)
- **Standards:** Conventional Commits, CommonMark, TOML configuration; Tera template engine for output
- **Authentication:** GitHub token via `GITHUB_TOKEN` env var, `--github-token` CLI arg, or `cliff.toml` config; supports `GITHUB_API_URL` override for GitHub Enterprise

**Configuration format (`cliff.toml`):**
```toml
[changelog]
header = "# Changelog\n"
body   = "{% for group, commits in commits | group_by(attribute='group') %}..."
footer = ""
trim   = true

[git]
conventional_commits = true
filter_unconventional = true
commit_parsers = [
  { message = "^feat", group = "Features" },
  { message = "^fix",  group = "Bug Fixes" },
]
```

GitHub Actions integration requires `fetch-depth: 0` on the checkout step to capture full history.

---

## Notes

### Gaps and Evolving Areas

1. **No universal release manifest schema.** There is no published ISO or IETF standard for a machine-readable release manifest (a JSON document capturing version, date, changelog entries, affected packages, CVEs patched, and asset hashes). The closest artefacts are GitHub's `Release` object and npm's `package.json`, but neither is a cross-platform standard. An opportunity exists to define and publish a JSON Schema for this.

2. **Monorepo changelog generation is immature.** Changesets, conventional-changelog, and git-cliff each handle monorepos differently and incompatibly. No single specification governs multi-package release notes; tooling in this space continues to evolve rapidly.

3. **AI-assisted release notes.** GitHub's `generate-notes` endpoint and similar features from GitLab and Linear are beginning to use LLMs to summarise PR descriptions and commit messages. No standardisation exists yet for prompting, output format, or accuracy guarantees.

4. **MCP integration.** The Model Context Protocol (November 2025 spec) provides the infrastructure for changelog generators to operate as AI-callable tools. No production MCP server for changelog generation has been standardised yet, but the architecture is now well-defined.

5. **GDPR and commit author data.** The intersection of GDPR personal data requirements and public git history is legally unsettled. Commit emails and names are personal data; automated changelog tools that display or store author information in published outputs should seek legal review for EU-facing products.

6. **Atom vs RSS.** Both feed formats remain in active use for distributing release notes. Atom (RFC 4287) is the formally standardised choice; RSS 2.0 has broader ecosystem support. Tools should consider supporting both for maximum compatibility.

7. **CalVer adoption.** A significant minority of projects (Ubuntu, pip, Black, etc.) use Calendar Versioning rather than SemVer. Changelog generators that assume SemVer for version-bump calculation will need extension points for CalVer projects.
