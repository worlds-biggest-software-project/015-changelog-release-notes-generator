# Changelog & Release Notes Generator — Feature & Functionality Survey

> Candidate #15 · Researched: 2026-04-22

## Solutions Analysed

| Tool | Type | Licence / Model | URL |
|------|------|-----------------|-----|
| semantic-release | Open source | MIT | https://github.com/semantic-release/semantic-release |
| Release Drafter | Open source (GitHub Action) | MIT | https://github.com/marketplace/actions/release-drafter |
| git-cliff | Open source | MIT / Apache-2.0 (dual) | https://git-cliff.org |
| release-please (Google) | Open source | Apache-2.0 | https://github.com/googleapis/release-please |
| changesets (Atlassian) | Open source | MIT | https://github.com/changesets/changesets |
| auto (Intuit) | Open source | MIT | https://github.com/intuit/auto |
| conventional-changelog | Open source | MIT | https://github.com/conventional-changelog/conventional-changelog |
| Beamer | Commercial SaaS | Proprietary | https://www.getbeamer.com |
| Headway | Commercial SaaS | Proprietary | https://headwayapp.co |
| Noticeable | Commercial SaaS | Proprietary | https://noticeable.io |
| WhatShipped | AI SaaS | Proprietary | https://whatshipped.dev |
| Changeish | Open source (AI-assisted) | MIT | https://github.com/itlackey/changeish |

---

## Feature Analysis by Solution

### semantic-release

**Core features**
- Fully automated version management: parses Conventional Commits to determine next SemVer version (MAJOR/MINOR/PATCH) without human input
- Changelog generation via `@semantic-release/changelog` plugin from structured commit history
- Automated GitHub/GitLab release creation and NPM/PyPI/crate publishing in a single pipeline
- Plugin-based architecture: 30+ community plugins for different VCS platforms, package registries, and notification channels
- `BREAKING CHANGE:` footer and `!` shorthand for major version bumps
- Multi-channel publishing: release to multiple npm distribution channels (latest, next, beta) with channel promotion

**Differentiating features**
- End-to-end automation: version bump + changelog + release tag + package publish in one CI step, with no manual decisions
- Multi-package channel model enables pre-release channels (beta, alpha) with separate subscriber groups

**UX patterns**
- Zero-configuration when Conventional Commits are followed; one `npx semantic-release` call in CI
- Configuration in `release.config.js` or `package.json` only needed for plugin customisation
- Dry-run mode (`--dry-run`) previews what version and notes would be generated without committing

**Integration points**
- GitHub, GitLab, Bitbucket (VCS)
- npm, PyPI, Cargo, Docker Hub, Maven (package registries via plugins)
- GitHub Actions, CircleCI, Jenkins, Travis CI
- Slack, email notifications via community plugins

**Known gaps**
- Requires Conventional Commits; generates nothing useful for projects with unstructured commit messages (affects ~90% of repos per ICSE 2025 research)
- No AI fallback for ambiguous or non-conforming commits
- Changelog is developer-facing only; no audience-specific output (user-facing vs. developer-facing)
- Monorepo support requires additional tooling (semantic-release-monorepo plugin; less mature than changesets)
- No issue tracker synthesis (commit-only; ignores linked Jira/Linear tickets)

**Licence / IP notes**
- MIT. No commercial restrictions.

---

### Release Drafter (GitHub Action)

**Core features**
- Automatically drafts GitHub release notes from merged PR metadata (title, labels, linked issues)
- Categorises PRs into changelog sections by label (e.g., `enhancement`, `bug`, `breaking-change`)
- Tracks contributors automatically in the release notes
- Version resolver: increments SemVer based on label category of included PRs
- Configurable via `.github/release-drafter.yml` committed to the repository
- Excludes PRs with specified labels (e.g., `skip-changelog`)

**Differentiating features**
- PR-metadata-centric rather than commit-message-centric; works well for teams that write good PR titles but not Conventional Commits
- Contributor acknowledgement is built-in; no additional tooling required

**UX patterns**
- Zero-touch after configuration: draft updated automatically after each merge
- Maintainer reviews and publishes the draft release at their cadence
- `.github/release-drafter.yml` is readable YAML with clear section definitions

**Integration points**
- GitHub-only (GitHub Actions)
- GitHub Issues and PR labels for categorisation
- No external VCS, issue tracker, or Slack integration

**Known gaps**
- GitHub-only; no GitLab, Bitbucket, or self-hosted Git support
- Relies on PR title quality; doesn't read commit bodies or diff content
- No AI classification; purely label-driven
- Output is GitHub release markdown only; no CHANGELOG.md, no user-facing audience variant
- No issue tracker synthesis beyond GitHub Issues

**Licence / IP notes**
- MIT. No commercial restrictions.

---

### git-cliff

**Core features**
- Highly configurable changelog generator written in Rust; parses Conventional Commits by default
- Custom commit parsers via TOML-based regex configuration (`[git] commit_parsers`)
- Template engine (Tera/Jinja2-compatible) for full control over changelog output format
- Postprocessors: regex replacements on the final rendered output (e.g., link PR numbers to GitHub)
- Tag range filtering: generate changelog for a specific version range or from the last tag
- Integration with git-cliff GitHub Action for automated changelog commits
- Configurable body/footer parsing for extracting metadata beyond the subject line

**Differentiating features**
- Most flexible changelog templating of any OSS tool; can produce any markdown or text format
- Rust implementation: fastest runtime; deterministic output suitable for large repositories
- Custom regex commit parsers enable partial adoption — works with semi-structured commits that don't fully conform to Conventional Commits

**UX patterns**
- Single binary; `git cliff` in any git repository
- `cliff.toml` configuration file with well-documented keys
- `--unreleased` flag for previewing changelog content before tagging

**Integration points**
- GitHub Actions (git-cliff-action)
- Any CI/CD via CLI
- No native issue tracker or collaboration tool integration

**Known gaps**
- Still requires some commit structure; full free-text commits produce poor output
- No AI fallback for ambiguous commits
- No issue tracker synthesis or PR body reading
- No user-facing audience variant; developer CHANGELOG only
- Template flexibility is powerful but requires upfront configuration investment

**Licence / IP notes**
- Dual MIT/Apache-2.0 licence. No commercial restrictions.

---

### release-please (Google)

**Core features**
- Maintains a continuously-updated "Release PR" that accumulates changelog entries as each Conventional Commit lands
- Automated SemVer version bumping based on Conventional Commit type analysis
- Multi-language support: Node.js, Python, Go, Java, Ruby, Rust, PHP, Terraform, and more (via release strategy plugins)
- Batch releases: merge the Release PR to trigger tag creation, GitHub release, and optionally package publishing
- Monorepo support: manages per-package version PRs in a single repository
- Configurable via `release-please-config.json` and `.release-please-manifest.json`

**Differentiating features**
- The Release PR model makes pending release content visible to the team before it ships; reviewable as a normal PR
- Broadest multi-language/multi-ecosystem support of any automated release tool
- Monorepo-native without additional plugins

**UX patterns**
- GitHub Action integration: bot creates and updates the Release PR automatically
- Team sees exactly what will be in the next release by looking at the open PR
- Merge the Release PR = ship the release; no other steps needed

**Integration points**
- GitHub (GitHub Actions, GitHub API for PR creation)
- GitLab support (experimental)
- Package publishing via separate workflow steps triggered by release tag

**Known gaps**
- Requires Conventional Commits; non-conforming commits are ignored or categorised as `misc`
- No AI fallback for unstructured commit messages
- No issue tracker synthesis
- No user-facing audience variant
- GitLab support is experimental and incomplete

**Licence / IP notes**
- Apache-2.0. No commercial restrictions.

---

### changesets (Atlassian)

**Core features**
- Contributor-driven changeset model: developers add `.changeset/*.md` files alongside code changes declaring what changed and the intended SemVer impact
- Automated version bumping and CHANGELOG.md generation from accumulated changeset files
- Per-package versioning in monorepos: each package gets its own independent version history
- `@changesets/cli` provides `changeset add`, `changeset version`, and `changeset publish` commands
- CI bot (`@changesets/action`) creates version PRs and publishes packages automatically
- Snapshot releases for pre-release testing

**Differentiating features**
- Human-declared impact model: developers intentionally document changes at contribution time, producing higher-quality changelogs than automated parsers
- Best-in-class monorepo support; purpose-built for multi-package repositories

**UX patterns**
- `changeset add` interactive CLI prompts developer to describe the change and select affected packages
- Bot comments on PRs lacking a changeset, prompting contributors to add one
- CHANGELOG.md is assembled from prose descriptions, not commit subjects — output reads like human writing

**Integration points**
- GitHub, GitLab via CI actions
- npm, Yarn workspaces for monorepo publishing
- GitHub Actions changesets bot for automated version PR creation

**Known gaps**
- Requires contributor discipline; teams that don't maintain the habit produce incomplete changelogs
- High friction for external contributors: PR authors must understand the changeset workflow
- Single-package repositories gain little advantage over simpler tools
- No AI to suggest changeset content or fill gaps when files are missing
- No user-facing audience variant

**Licence / IP notes**
- MIT. No commercial restrictions.

---

### auto (Intuit)

**Core features**
- Label-based SemVer versioning: PR labels (`major`, `minor`, `patch`, `skip-release`) drive version decisions
- Changelog generation from PR titles grouped by label category
- Plugin system for extending release workflow (npm, PyPI, Gradle, GitHub Releases, Slack, etc.)
- Monorepo support via `@auto-it/monorepo-changelog` plugin
- Shipped labels: `shipped`, `closed-prerelease-major` for managing PR history sections
- Canary releases: publish pre-release versions from feature branches for testing

**Differentiating features**
- Label-driven workflow matches team processes that use PR labels for project management
- Canary releases from feature branches without version commit overhead
- Broad plugin ecosystem comparable to semantic-release

**UX patterns**
- `auto shipit` is the single command that handles versioning, changelog, and publishing
- No commit format requirements; only PR label discipline needed
- Interactive `auto label` command for bulk-labelling PRs via CLI

**Integration points**
- GitHub, GitLab (partial)
- npm, PyPI, Cargo, Gradle via plugins
- Slack, Microsoft Teams notifications
- Jenkins, GitHub Actions, CircleCI

**Known gaps**
- Relies on PR label consistency; inconsistently labelled PRs produce inaccurate version bumps
- No AI classification of commits or PRs
- No issue tracker synthesis
- Less popular than semantic-release; smaller community and plugin maintenance

**Licence / IP notes**
- MIT. No commercial restrictions.

---

### Beamer

**Core features**
- User-facing changelog / product announcement SaaS with in-app widget and standalone page
- Audience targeting: show specific announcements to specific user segments by plan, role, or attribute
- NPS survey integration alongside release announcements
- Reaction and emoji feedback on individual changelog entries
- Email and push notification delivery of new announcements to subscribed users
- Analytics: views, click-through rates, and engagement metrics per announcement
- Roadmap and idea collection modules (beyond changelog scope)

**Differentiating features**
- Most advanced audience targeting of any changelog SaaS; segment users by custom attributes
- In-app widget with unread badge drives user awareness of new features without email
- NPS survey adjacent to announcements correlates feature delivery with satisfaction scores

**UX patterns**
- WYSIWYG editor for announcement authoring; no markdown or coding required
- In-app widget configuration via embed code snippet; no backend integration needed
- Analytics dashboard shows which announcements drove the most engagement

**Integration points**
- JavaScript embed snippet for any web app
- Segment, Intercom, HubSpot for user attribute syncing
- Zapier / API for triggering announcements from external events
- Slack, email for team notifications on publication

**Known gaps**
- No git integration; announcements are manually authored, not generated from commits
- No developer-facing CHANGELOG.md generation
- No bridge between developer release tooling and user-facing announcements
- Limited development velocity reported by users; feature additions have slowed
- Pricing ($49–$499/month) is high for small teams

**Licence / IP notes**
- Proprietary SaaS. No IP concerns for feature design.

---

### WhatShipped

**Core features**
- AI-powered release notes generation from git commit ranges
- Handles large commit batches (~100 commits) via parallel LLM processing with result merging
- Produces human-readable summaries rather than raw commit-message lists
- Cloud SaaS; connects to GitHub repository via OAuth
- Output suitable for GitHub releases and developer-facing changelogs

**Differentiating features**
- Parallel batch processing for large commit ranges is architecturally practical for real-world release sizes
- Requires no commit convention — works with free-text commit messages

**UX patterns**
- Web UI: select repository, specify commit range, click generate
- No CLI or CI integration; web-only workflow

**Integration points**
- GitHub via OAuth
- GitHub Releases as output target

**Known gaps**
- No CLI, no CI/CD integration; can't be automated in a pipeline
- No issue tracker synthesis (Jira, Linear, GitHub Issues)
- No audience-specific output (developer vs. user-facing variant)
- Limited configuration for output format or template customisation
- Cloud-only; no self-hosted option

**Licence / IP notes**
- Proprietary SaaS. No IP concerns.

---

### Changeish

**Core features**
- AI-powered changelog content generation using Ollama for local LLM execution
- Privacy-focused: runs entirely locally without sending code to external APIs
- Cloud-agnostic: works with any Ollama-compatible model (Llama 3, Mistral, Phi, etc.)
- CLI-based; generates changelog entries for uncommitted or specified commit ranges
- Basic Conventional Commits-compatible output format

**Differentiating features**
- Local execution via Ollama is the only AI changelog tool with genuine privacy guarantee
- Model-agnostic: swap underlying LLM without tool changes

**UX patterns**
- Single CLI command; minimal configuration
- Output to stdout or file

**Integration points**
- Ollama (local model runtime)
- Any CI/CD via CLI
- No native VCS platform (GitHub/GitLab) integration

**Known gaps**
- Local model quality may be lower than hosted LLM APIs (GPT-4, Claude) for nuanced summarisation
- No issue tracker synthesis
- No team collaboration or shared output destination
- No audience-specific output variants
- Early-stage tool; limited production validation

**Licence / IP notes**
- MIT. No commercial restrictions.

---

## Cross-Cutting Feature Themes

### Table-Stakes Features

Any viable solution in this space must provide:

- Changelog generation from git commit history without requiring manual authorship
- GitHub and GitLab integration (webhook/action or CLI)
- SemVer version determination logic (MAJOR/MINOR/PATCH)
- Categorisation of changes by type (features, bug fixes, breaking changes, security)
- Configurable output format (markdown at minimum; HTML optional)
- CI/CD integration via CLI or GitHub Action
- Filtering mechanism to exclude internal/maintenance commits from user-visible output
- Plain-text format output compatible with CHANGELOG.md convention (Keep a Changelog v1.1.0)

### Differentiating Features

Capabilities that provide competitive advantage:

- **AI classification of free-text commits**: generating structured changelogs from repositories that don't follow Conventional Commits (affects ~90% of projects)
- **Multi-audience output**: generating separate developer-facing and user-facing variants from the same commit history
- **Issue tracker synthesis**: fetching linked Jira/Linear/GitHub Issues context and incorporating business-level descriptions into release notes
- **PR body reading**: using the pull request description (not just title and labels) as source material for richer notes
- **Local/private LLM execution**: generating notes without sending code to external APIs (Changeish approach; enterprise security requirement)
- **Monorepo per-package changelog**: independent version and changelog tracking per package in a monorepo (changesets, release-please)
- **In-app user-facing announcement delivery**: widget and notification delivery of release notes to end users (Beamer/Headway approach)

### Underserved Areas / Opportunities

- **The developer-to-user translation gap**: every OSS tool produces developer-facing changelogs. No open-source tool generates both a `CHANGELOG.md` for developers and a "What's New" announcement for end users from the same source. This is the most commercially valuable unserved use case.
- **Issue tracker as primary source**: all OSS tools treat git history as the source of truth. For product teams, the Jira/Linear ticket is the source of truth — the commit is an implementation detail. No tool synthesises ticket context into release notes.
- **Working with poor commit history**: ~90% of projects have non-conforming commits, 14% are empty, 66% are minimal. Rule-based tools silently produce empty or useless changelogs for these projects. AI that recovers from low-quality input signals is an unmet need.
- **Role-aware output variants**: SmartNote (2025 research prototype) introduced personalisation concepts. No production open-source tool generates developer / admin / end-user variants of the same release note.
- **Audit trail for compliance**: engineering managers and compliance officers need traceability from release notes back to specific commits, PRs, and tickets. No tool provides this link bidirectionally.

### AI-Augmentation Candidates

- **Free-text commit classification**: LLM reads raw commit messages, diff summary, and PR description to infer type (feature/fix/breaking/internal), scope, and user impact without requiring any commit format convention.
- **Audience-aware summarisation**: LLM generates two or more output variants from the same change set — technical details for developers, benefit statements for end users — filtered appropriately (internal refactors omitted from user notes, API changes expanded for developer notes).
- **Issue tracker context synthesis**: LLM reads the linked Jira/Linear ticket title, description, and acceptance criteria to produce a business-context-aware release note entry rather than a code-context-aware one.
- **Commit quality improvement feedback**: LLM flags commits with poor messages during PR review and suggests improved descriptions, improving future changelog quality as a side effect.
- **Cross-release summary generation**: LLM produces a "quarterly summary" or "what changed since version X" narrative across multiple releases for stakeholder communication.

---

## Legal & IP Summary

No copyright, patent, or licence conflicts were identified that would prevent building in this space. All open-source tools surveyed are permissively licenced (MIT or Apache-2.0). Specific notes:

- **git-cliff (MIT/Apache-2.0 dual)**: safe for commercial embedding and derivative works under either licence.
- **semantic-release, changesets, auto, release-please**: all MIT or Apache-2.0; no restrictions.
- **conventional-changelog (MIT)**: safe for embedding as a parsing library.

Commercial SaaS tools (Beamer, Headway, WhatShipped) were analysed for feature patterns only; no code or proprietary text was reproduced.

LLM-based commit classification and summarisation are generic AI techniques. The SmartNote paper (arXiv:2505.17977, 2025) describes a research prototype; academic paper findings can be used as design inspiration without IP concern. No active software patents were identified covering the specific techniques surveyed as of April 2026.

---

## Recommended Feature Scope

**Must-have (MVP)**
- AI-based commit classification from free-text messages (no Conventional Commits requirement)
- CHANGELOG.md generation in Keep a Changelog v1.1.0 format
- GitHub and GitLab integration via CLI and GitHub Action
- SemVer version suggestion based on classified change types
- Configurable category labels and output sections
- Per-commit filtering: exclude commits matching configurable patterns (merge commits, dependency bumps)

**Should-have (v1.1)**
- Dual-audience output: developer CHANGELOG and user-facing "What's New" from the same source
- GitHub Issues and PR body reading for richer source material beyond commit messages
- Jira and Linear issue tracker integration: fetch ticket context for linked issue numbers
- Historical changelog comparison: explain what changed between two versions in plain language
- Local LLM execution option via Ollama for privacy-sensitive environments

**Nice-to-have (backlog)**
- Role-aware output variants: developer / admin / end-user release note editions
- In-app announcement widget embed for user-facing changelog delivery
- Monorepo per-package independent changelog and versioning
- Slack and email delivery of release notes on tag/publish event
- Compliance audit trail: bidirectional links from release note entries to commits, PRs, and tickets
