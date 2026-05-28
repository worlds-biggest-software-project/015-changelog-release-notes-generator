# Changelog & Release Notes Generator — Phased Development Plan

> Project: 015-changelog-release-notes-generator · Created: 2026-05-11
> Purpose: Provide sufficient detail for Claude Code (Opus) to implement each phase end-to-end.

---

## Technology Decisions

| Concern | Choice | Rationale |
|---------|--------|-----------|
| Language | TypeScript (Node.js 20+) | Largest ecosystem overlap with GitHub/GitLab/npm tooling; first-class Octokit SDK; LLM SDK support (Anthropic, OpenAI) |
| Runtime | Node.js 20 LTS | Native ESM, built-in test runner, stable fetch API |
| Database | PostgreSQL 16 + JSONB | Hybrid model (Data Model Suggestion 3) — relational core with JSONB for provider-specific and AI-generated data; single database, no event store infrastructure |
| ORM | Drizzle ORM | Type-safe SQL, zero runtime overhead, first-class JSONB support, migration tooling built-in |
| CLI Framework | Commander.js | De facto standard for Node.js CLIs; composable subcommands, built-in help generation |
| LLM Integration | Anthropic SDK (`@anthropic-ai/sdk`) primary; pluggable provider interface for OpenAI/Ollama | Claude produces the best structured output for classification tasks; Ollama support addresses privacy-sensitive environments |
| Git Integration | `simple-git` (Node.js) | Mature, promise-based, covers log/diff/tag operations without shelling out |
| GitHub API | Octokit (`@octokit/rest` + `@octokit/auth-app`) | Official SDK; typed responses; pagination helpers; GitHub App auth |
| GitLab API | `@gitbeaker/rest` | Most maintained GitLab SDK for Node.js; REST-based |
| Jira API | `jira.js` | TypeScript-native; covers REST v3 endpoints including project versions |
| Linear API | `@linear/sdk` | Official SDK; code-generated from GraphQL schema |
| Template Engine | Handlebars | Simpler than Tera for end-user customization; used by conventional-changelog and Release Drafter; familiar syntax |
| Output Format | CommonMark 0.31.2 (primary), HTML, JSON, Atom (RFC 4287) | CommonMark for CHANGELOG.md; HTML for web publishing; JSON for programmatic consumers; Atom for feed subscription |
| Testing | Vitest | Fast, ESM-native, built-in coverage, compatible with Node.js test patterns |
| Package Manager | pnpm | Strict dependency resolution; workspace support for potential monorepo structure |
| CI/CD | GitHub Actions (primary), GitLab CI (secondary) | Matches target user base; Action published to GitHub Marketplace |
| Configuration | `changelog-gen.config.ts` / `.changelog-gen.json` with JSON Schema validation | TypeScript config for IDE autocomplete; JSON Schema for validation and documentation |
| Versioning Scheme | SemVer 2.0.0 (own releases); support for SemVer + CalVer in target repos | SemVer is the dominant standard; CalVer support covers Ubuntu/pip-style projects |

### Project Structure

```
changelog-gen/
├── src/
│   ├── cli/
│   │   ├── index.ts                  # CLI entry point (Commander.js)
│   │   ├── commands/
│   │   │   ├── generate.ts           # Main changelog generation command
│   │   │   ├── classify.ts           # Classify commits without generating
│   │   │   ├── publish.ts            # Publish to channels
│   │   │   ├── init.ts               # Initialize config for a repo
│   │   │   └── version.ts            # Calculate next version
│   │   └── formatters/
│   │       ├── terminal.ts           # Terminal output formatting
│   │       └── progress.ts           # Progress indicators
│   ├── core/
│   │   ├── config.ts                 # Configuration loading and validation
│   │   ├── types.ts                  # Core type definitions
│   │   ├── errors.ts                 # Error types and handling
│   │   └── logger.ts                 # Structured logging
│   ├── git/
│   │   ├── repository.ts             # Git repository operations
│   │   ├── commit-parser.ts          # Commit message parsing
│   │   ├── tag-resolver.ts           # Tag and version range resolution
│   │   └── diff-analyzer.ts          # Diff statistics extraction
│   ├── classifier/
│   │   ├── index.ts                  # Classifier orchestrator
│   │   ├── conventional.ts           # Conventional Commits rule-based parser
│   │   ├── ai-classifier.ts          # LLM-based classification
│   │   ├── prompts.ts                # LLM prompt templates
│   │   └── types.ts                  # Classification types
│   ├── providers/
│   │   ├── index.ts                  # Provider registry
│   │   ├── github.ts                 # GitHub API integration
│   │   ├── gitlab.ts                 # GitLab API integration
│   │   ├── jira.ts                   # Jira API integration
│   │   ├── linear.ts                 # Linear API integration
│   │   └── types.ts                  # Provider interface types
│   ├── generator/
│   │   ├── index.ts                  # Entry generation orchestrator
│   │   ├── entry-builder.ts          # Builds changelog entries from classified commits
│   │   ├── audience-writer.ts        # Generates audience-specific variants
│   │   ├── version-calculator.ts     # SemVer/CalVer next-version logic
│   │   └── grouper.ts               # Groups entries by Keep a Changelog categories
│   ├── renderer/
│   │   ├── index.ts                  # Renderer orchestrator
│   │   ├── markdown.ts               # CommonMark renderer
│   │   ├── html.ts                   # HTML renderer
│   │   ├── json.ts                   # JSON renderer
│   │   ├── atom.ts                   # Atom feed renderer (RFC 4287)
│   │   └── templates/
│   │       ├── default.hbs           # Default Keep a Changelog template
│   │       ├── user-facing.hbs       # User-facing "What's New" template
│   │       └── compact.hbs           # Compact single-line-per-entry template
│   ├── publisher/
│   │   ├── index.ts                  # Publisher orchestrator
│   │   ├── github-release.ts         # Publish to GitHub Releases
│   │   ├── gitlab-release.ts         # Publish to GitLab Releases
│   │   ├── file-writer.ts            # Write CHANGELOG.md to disk
│   │   ├── slack.ts                  # Post to Slack webhook
│   │   └── types.ts                  # Publisher interface types
│   ├── db/
│   │   ├── schema.ts                 # Drizzle ORM schema definitions
│   │   ├── migrations/               # Database migration files
│   │   ├── client.ts                 # Database client setup
│   │   └── queries.ts                # Reusable query builders
│   └── action/
│       ├── index.ts                  # GitHub Action entry point
│       └── inputs.ts                 # Action input parsing
├── templates/                        # User-customizable Handlebars templates
├── test/
│   ├── fixtures/                     # Git history fixtures, mock API responses
│   ├── unit/                         # Unit tests
│   ├── integration/                  # Integration tests (with test DB)
│   └── e2e/                          # End-to-end tests (with real git repos)
├── action.yml                        # GitHub Action metadata
├── package.json
├── tsconfig.json
├── vitest.config.ts
├── drizzle.config.ts
├── changelog-gen.schema.json         # JSON Schema for configuration
└── README.md
```

---

## Phase 1: Project Scaffolding & Core Types

### Purpose
Establish the project skeleton, define all core types, configure the build system, and create the CLI entry point. This phase produces a runnable (but functionally empty) CLI that validates configuration and prints help.

### Tasks

#### 1.1 — Initialize Project & Build System
**What**: Create the npm package, configure TypeScript, ESM, pnpm, and Vitest.

**Design**:
```typescript
// package.json (key fields)
{
  "name": "changelog-gen",
  "type": "module",
  "bin": { "changelog-gen": "./dist/cli/index.js" },
  "engines": { "node": ">=20.0.0" },
  "exports": { ".": "./dist/core/index.js" }
}

// tsconfig.json (key fields)
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "declaration": true,
    "sourceMap": true
  }
}
```

**Testing**:
- `test-build-succeeds`: `pnpm build` exits 0 with no TypeScript errors
- `test-cli-runs`: `node dist/cli/index.js --help` prints usage and exits 0
- `test-esm-import`: `import { ... } from 'changelog-gen'` resolves without errors

#### 1.2 — Define Core Type System
**What**: Define all domain types used across the codebase, aligned with the Hybrid Relational + JSONB data model (Suggestion 3).

**Design**:
```typescript
// src/core/types.ts

export type VCSProvider = 'github' | 'gitlab' | 'bitbucket' | 'local';
export type IssueProvider = 'github' | 'gitlab' | 'jira' | 'linear';
export type CommitType = 'feat' | 'fix' | 'chore' | 'docs' | 'refactor' | 'perf' | 'test' | 'ci' | 'build' | 'style' | 'breaking';
export type ChangelogCategory = 'Added' | 'Changed' | 'Deprecated' | 'Removed' | 'Fixed' | 'Security';
export type ClassificationMethod = 'conventional_commits' | 'ai_llm' | 'manual' | 'label_based';
export type Audience = 'developer' | 'end_user' | 'admin' | 'security';
export type OutputFormat = 'markdown' | 'html' | 'json' | 'atom' | 'rss' | 'plaintext';
export type VersionScheme = 'semver' | 'calver' | 'custom';
export type ReleaseStatus = 'draft' | 'published' | 'yanked';
export type LinkType = 'authored_in' | 'fixes' | 'references' | 'closes';

export interface SemanticVersion {
  major: number;
  minor: number;
  patch: number;
  prerelease: string | null;
  buildMetadata: string | null;
  scheme: VersionScheme;
  raw: string;
}

export interface CommitInfo {
  sha: string;
  messageSubject: string;
  messageBody: string | null;
  committedAt: Date;
  isMergeCommit: boolean;
  authorInfo: AuthorInfo;
  diffStats: DiffStats | null;
}

export interface AuthorInfo {
  name: string | null;
  email: string | null;
  providerUsername: string | null;
  providerUserId: string | null;
  avatarUrl: string | null;
  gdprErased?: boolean;
}

export interface DiffStats {
  filesChanged: number;
  insertions: number;
  deletions: number;
  files: Array<{ path: string; insertions: number; deletions: number }>;
}

export interface CommitClassification {
  type: CommitType;
  scope: string | null;
  isBreaking: boolean;
  isInternal: boolean;
  confidence: number | null;       // 0.0-1.0; null if rule-based
  method: ClassificationMethod;
  model: string | null;            // e.g. "claude-sonnet-4-20250514"
  classifiedAt: Date;
  userImpactSummary: string | null;
  developerSummary: string | null;
  previousClassifications: CommitClassification[];
}

export interface SourceItem {
  id: string;
  itemType: 'pull_request' | 'issue' | 'ticket';
  provider: IssueProvider;
  providerItemId: string;
  title: string;
  body: string | null;
  status: string;
  authorInfo: AuthorInfo;
  metadata: Record<string, unknown>;
}

export interface ChangelogEntry {
  id: string;
  category: ChangelogCategory;
  bodyMarkdown: string;
  displayOrder: number;
  isBreaking: boolean;
  isSecurity: boolean;
  isHighlight: boolean;
  sources: EntrySources;
  generation: GenerationMetadata;
  audienceVariants: Record<Audience, AudienceVariant>;
}

export interface EntrySources {
  commitShas: string[];
  pullRequestIds: string[];
  issueIds: string[];
}

export interface GenerationMetadata {
  method: 'ai_generated' | 'manual' | 'template_based';
  model: string | null;
  promptHash: string | null;
  generatedAt: Date;
  confidence: number | null;
  editedByHuman: boolean;
}

export interface AudienceVariant {
  bodyMarkdown: string;
  isVisible: boolean;
  generatedAt: Date;
}

export interface ReleaseInfo {
  id: string;
  tagName: string;
  version: SemanticVersion;
  releaseDate: string;         // ISO 8601 date YYYY-MM-DD
  title: string | null;
  status: ReleaseStatus;
  isPrerelease: boolean;
  commitRange: { fromSha: string; toSha: string; commitCount: number };
  entries: ChangelogEntry[];
}

// Keep a Changelog v1.1.0 category mapping
export const COMMIT_TYPE_TO_CATEGORY: Record<CommitType, ChangelogCategory | null> = {
  feat: 'Added',
  fix: 'Fixed',
  breaking: 'Changed',
  perf: 'Changed',
  refactor: null,         // internal; excluded from user-facing
  chore: null,
  docs: null,
  test: null,
  ci: null,
  build: null,
  style: null,
};
```

**Testing**:
- `test-types-compile`: All types compile without errors; no `any` escapes
- `test-category-mapping-complete`: Every `CommitType` has a mapping entry
- `test-version-schema`: `SemanticVersion` correctly represents "1.2.3-alpha.1+build.456"

#### 1.3 — Configuration System
**What**: Implement configuration loading from file, environment variables, and CLI flags with JSON Schema validation.

**Design**:
```typescript
// src/core/config.ts

export interface ChangelogGenConfig {
  repository: {
    provider: VCSProvider;
    name: string;                 // e.g. "my-org/my-repo"
    defaultBranch: string;        // default: "main"
    isMonorepo: boolean;          // default: false
  };
  llm: {
    provider: 'anthropic' | 'openai' | 'ollama';
    model: string;                // default: "claude-sonnet-4-20250514"
    apiKey?: string;              // from env: ANTHROPIC_API_KEY, OPENAI_API_KEY
    baseUrl?: string;             // for Ollama: "http://localhost:11434"
    maxTokens: number;            // default: 4096
  };
  classification: {
    method: 'auto' | 'conventional_only' | 'ai_only';  // default: "auto"
    confidenceThreshold: number;  // default: 0.7; below this, flag for review
    commitFilterPatterns: string[];  // default: ["^Merge"]
  };
  output: {
    format: OutputFormat;         // default: "markdown"
    audiences: Audience[];        // default: ["developer"]
    templateName: string;         // default: "default"
    includeContributors: boolean; // default: true
    includePrLinks: boolean;      // default: true
    includeIssueLinks: boolean;   // default: true
  };
  providers: {
    github?: { token: string };
    gitlab?: { token: string; apiUrl?: string };
    jira?: { apiBaseUrl: string; email: string; token: string; projectKey: string };
    linear?: { apiKey: string; teamKey?: string };
  };
  versionScheme: VersionScheme;   // default: "semver"
}

export function loadConfig(configPath?: string): ChangelogGenConfig;
export function validateConfig(config: unknown): asserts config is ChangelogGenConfig;
export function mergeWithDefaults(partial: Partial<ChangelogGenConfig>): ChangelogGenConfig;
```

Error handling: throw `ConfigurationError` with field path and human-readable message. Environment variable override convention: `CHANGELOG_GEN_LLM_API_KEY`, `GITHUB_TOKEN`, `GITLAB_TOKEN`.

**Testing**:
- `test-load-default-config`: Loading with no file produces valid defaults
- `test-env-override`: `GITHUB_TOKEN` env var populates `providers.github.token`
- `test-invalid-config-throws`: Missing required fields throw `ConfigurationError` with field path
- `test-json-schema-validation`: Config file validated against `changelog-gen.schema.json`
- `test-merge-partial-config`: Partial config correctly merged with defaults

#### 1.4 — CLI Entry Point
**What**: Set up Commander.js with subcommands (`generate`, `classify`, `publish`, `init`, `version`) and global options.

**Design**:
```typescript
// src/cli/index.ts
import { Command } from 'commander';

const program = new Command()
  .name('changelog-gen')
  .description('AI-powered changelog and release notes generator')
  .version(packageVersion);

program
  .command('generate')
  .description('Generate changelog from git history')
  .option('--since <ref>', 'Start ref (tag, SHA, or "last-release")')
  .option('--until <ref>', 'End ref (default: HEAD)', 'HEAD')
  .option('--output <path>', 'Output file path (default: CHANGELOG.md)')
  .option('--format <fmt>', 'Output format: markdown|html|json|atom', 'markdown')
  .option('--audience <audience>', 'Target audience: developer|end_user|admin', 'developer')
  .option('--dry-run', 'Preview without writing files')
  .option('--config <path>', 'Path to config file')
  .action(generateCommand);

program
  .command('init')
  .description('Initialize changelog-gen configuration for this repository')
  .action(initCommand);

// ... classify, publish, version subcommands
```

**Testing**:
- `test-cli-help`: `changelog-gen --help` lists all subcommands
- `test-cli-generate-help`: `changelog-gen generate --help` lists all options
- `test-cli-unknown-command`: Unknown subcommand prints error and exits 1
- `test-cli-version`: `changelog-gen --version` prints package version

---

## Phase 2: Git History Ingestion & Conventional Commits Parsing

### Purpose
Read git commit history between two refs, parse commit messages, extract diff statistics, and classify commits using Conventional Commits rules. This phase delivers the first useful output: a rule-based changelog from well-formatted commit history.

### Tasks

#### 2.1 — Git Repository Operations
**What**: Implement git history reading, tag listing, and commit range resolution using `simple-git`.

**Design**:
```typescript
// src/git/repository.ts
import simpleGit, { SimpleGit } from 'simple-git';

export class GitRepository {
  private git: SimpleGit;

  constructor(workingDir: string);

  /** List all tags sorted by version (SemVer-aware) */
  async listTags(): Promise<TagInfo[]>;

  /** Get commits between two refs (exclusive start, inclusive end) */
  async getCommits(from: string | null, to: string): Promise<CommitInfo[]>;

  /** Resolve a ref (tag name, SHA, branch, "HEAD") to a full SHA */
  async resolveRef(ref: string): Promise<string>;

  /** Get the latest tag reachable from HEAD */
  async getLatestTag(): Promise<TagInfo | null>;

  /** Get diff stats for a single commit */
  async getDiffStats(sha: string): Promise<DiffStats>;
}

export interface TagInfo {
  name: string;          // e.g. "v1.2.3"
  sha: string;
  date: Date;
  version: SemanticVersion | null;  // parsed if tag matches SemVer pattern
}
```

Error handling: throw `GitError` for missing repo, invalid refs, and detached HEAD states. Handle shallow clones (GitHub Actions default) by detecting `--depth` and warning.

**Testing**:
- `test-list-tags-semver-sorted`: Tags v1.0.0, v1.1.0, v2.0.0 sorted correctly
- `test-get-commits-range`: Commits between v1.0.0..v1.1.0 returns correct set
- `test-resolve-ref-tag`: `resolveRef("v1.0.0")` returns full SHA
- `test-resolve-ref-head`: `resolveRef("HEAD")` returns current SHA
- `test-shallow-clone-warning`: Shallow clone detected; logs warning about incomplete history
- `test-empty-range`: No commits between identical refs returns empty array
- `test-merge-commit-detection`: Merge commits correctly identified via parent count

#### 2.2 — Conventional Commits Parser
**What**: Parse commit messages following Conventional Commits v1.0.0 specification, extracting type, scope, description, body, footers, and breaking change indicators.

**Design**:
```typescript
// src/classifier/conventional.ts

export interface ConventionalParseResult {
  isConventional: boolean;       // true if message matches CC format
  type: CommitType | null;
  scope: string | null;
  description: string | null;
  body: string | null;
  footers: Array<{ key: string; value: string }>;
  isBreaking: boolean;           // `!` suffix or BREAKING CHANGE footer
  breakingDescription: string | null;
}

/**
 * Parse a commit message per Conventional Commits v1.0.0.
 * Pattern: ^(?<type>\w+)(?:\((?<scope>[^)]+)\))?(?<breaking>!)?:\s*(?<description>.+)
 */
export function parseConventionalCommit(message: string): ConventionalParseResult;

/**
 * Classify a commit using Conventional Commits rules.
 * Returns null if the message does not match CC format.
 */
export function classifyConventional(commit: CommitInfo): CommitClassification | null;
```

Handles edge cases from ICSE 2025 study: multi-scope (`feat(auth,api):`), exclamation-mark breaking indicator (`feat!:`), `BREAKING CHANGE:` and `BREAKING-CHANGE:` footers, multiline bodies with `\n\n` separation.

**Testing**:
- `test-parse-simple-feat`: `"feat: add login"` -> type=feat, scope=null, breaking=false
- `test-parse-scoped`: `"fix(parser): handle null"` -> type=fix, scope="parser"
- `test-parse-breaking-exclamation`: `"feat!: remove v1 API"` -> breaking=true
- `test-parse-breaking-footer`: Message with `BREAKING CHANGE: removed X` footer -> breaking=true
- `test-parse-body-and-footer`: Multi-line message with body and footers extracted correctly
- `test-parse-non-conventional`: `"Update readme"` -> isConventional=false
- `test-parse-multi-scope`: `"feat(auth,api): add SSO"` -> scope="auth,api"
- `test-classify-returns-null-for-freetext`: Non-CC message returns null classification

#### 2.3 — Commit Classifier Orchestrator
**What**: Orchestrate classification by trying Conventional Commits first, falling back to a placeholder for AI (Phase 3), and applying commit filter patterns.

**Design**:
```typescript
// src/classifier/index.ts

export class CommitClassifier {
  constructor(config: ChangelogGenConfig['classification']);

  /**
   * Classify a batch of commits.
   * Strategy based on config.method:
   *   'conventional_only' — CC parser only; unmatched commits get type=null
   *   'ai_only'           — all commits sent to AI (Phase 3)
   *   'auto'              — CC parser first; AI fallback for non-CC commits
   */
  async classifyAll(commits: CommitInfo[]): Promise<ClassifiedCommit[]>;

  /** Apply filter patterns to exclude commits (merge commits, deps, etc.) */
  filterCommits(commits: CommitInfo[]): CommitInfo[];
}

export interface ClassifiedCommit {
  commit: CommitInfo;
  classification: CommitClassification | null;
  isFiltered: boolean;
}
```

**Testing**:
- `test-auto-mode-cc-first`: CC-formatted commits classified by parser; others left unclassified
- `test-filter-merge-commits`: Commits matching `^Merge` pattern excluded
- `test-filter-custom-pattern`: Custom pattern `^chore\(deps\)` excludes dependency bumps
- `test-conventional-only-mode`: Non-CC commits returned with null classification
- `test-classify-batch-ordering`: Output order matches input order

#### 2.4 — Basic Changelog Renderer (Markdown)
**What**: Render classified commits into Keep a Changelog v1.1.0 format markdown.

**Design**:
```typescript
// src/renderer/markdown.ts

export class MarkdownRenderer {
  constructor(private templateEngine: Handlebars);

  /**
   * Render a release as Keep a Changelog v1.1.0 markdown.
   * Groups entries by category (Added, Changed, Fixed, etc.).
   * ISO 8601 date format. Newest version first.
   */
  render(release: ReleaseInfo, options: RenderOptions): string;

  /**
   * Render full changelog (multiple releases).
   * Prepends "# Changelog" header and [Unreleased] section.
   */
  renderFull(releases: ReleaseInfo[], unreleased: ChangelogEntry[]): string;
}

export interface RenderOptions {
  audience: Audience;
  includeContributors: boolean;
  includePrLinks: boolean;
  includeIssueLinks: boolean;
  templateName: string;
}
```

Output format example:
```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [1.3.0] - 2026-05-11

### Added

- SSO login support via OpenID Connect (#42)
- Bulk user import from CSV (#38)

### Fixed

- Fix null pointer in date parser (#41)
- Correct timezone handling for EU regions (#39)

### Security

- Upgrade lodash to 4.17.21 to patch CVE-2021-23337 (#40)
```

**Testing**:
- `test-render-single-release`: One release with entries in all six KaC categories
- `test-render-empty-categories-omitted`: Categories with no entries are not rendered
- `test-render-iso-date`: Date formatted as YYYY-MM-DD
- `test-render-breaking-section`: Breaking changes highlighted with "BREAKING" prefix
- `test-render-pr-links`: PR numbers linked to provider URLs when enabled
- `test-render-full-changelog`: Multiple releases rendered newest-first with Unreleased section

---

## Phase 3: AI-Powered Commit Classification

### Purpose
Integrate LLM-based classification for free-text commits that do not follow Conventional Commits. This is the core differentiator — making the tool work for the ~90% of projects that lack commit conventions.

### Tasks

#### 3.1 — LLM Provider Interface
**What**: Define a pluggable LLM provider interface and implement the Anthropic (Claude) provider.

**Design**:
```typescript
// src/classifier/ai-classifier.ts

export interface LLMProvider {
  readonly name: string;
  classify(input: ClassificationInput): Promise<ClassificationOutput>;
  classifyBatch(inputs: ClassificationInput[], batchSize?: number): Promise<ClassificationOutput[]>;
}

export interface ClassificationInput {
  messageSubject: string;
  messageBody: string | null;
  diffStats: DiffStats | null;
  prTitle: string | null;
  prBody: string | null;
  filePaths: string[];
}

export interface ClassificationOutput {
  type: CommitType;
  scope: string | null;
  isBreaking: boolean;
  isInternal: boolean;
  confidence: number;              // 0.0-1.0
  userImpactSummary: string;       // one sentence: what this means for users
  developerSummary: string;        // one sentence: technical description
}

export class AnthropicClassifier implements LLMProvider {
  constructor(apiKey: string, model: string);
  async classify(input: ClassificationInput): Promise<ClassificationOutput>;
  async classifyBatch(inputs: ClassificationInput[], batchSize?: number): Promise<ClassificationOutput[]>;
}
```

Batch processing: send up to 10 commits per API call using tool_use for structured output. Rate limiting: respect Anthropic API rate limits with exponential backoff. Cost tracking: log token usage per batch for cost visibility.

**Testing**:
- `test-classify-feature-commit`: `"Add user authentication"` classified as feat with high confidence
- `test-classify-bugfix-commit`: `"Fix crash on startup"` classified as fix
- `test-classify-breaking-change`: `"Remove deprecated v1 endpoints"` classified as breaking
- `test-classify-internal-refactor`: `"Refactor database connection pool"` classified as refactor with isInternal=true
- `test-classify-empty-message`: Empty or minimal message handled gracefully (low confidence)
- `test-classify-batch-parallel`: 50 commits classified in parallel batches of 10
- `test-classify-rate-limit-retry`: 429 response triggers exponential backoff

#### 3.2 — Classification Prompt Engineering
**What**: Design and implement the LLM prompts for commit classification, optimized for structured output.

**Design**:
```typescript
// src/classifier/prompts.ts

export function buildClassificationPrompt(input: ClassificationInput): {
  system: string;
  user: string;
  tools: ToolDefinition[];
};

// System prompt structure:
// 1. Role: "You are a software release note classifier..."
// 2. Type definitions: list of valid CommitType values with descriptions
// 3. Breaking change criteria: API removal, behavior change, config format change
// 4. Internal vs. external: refactors, CI, tests = internal; features, fixes = external
// 5. Confidence calibration: 0.9+ for clear cases; 0.5-0.7 for ambiguous
// 6. Output format: use the classify_commit tool

// Tool definition for structured output:
export const CLASSIFY_COMMIT_TOOL: ToolDefinition = {
  name: 'classify_commit',
  description: 'Classify a git commit into a type with impact summaries',
  input_schema: {
    type: 'object',
    properties: {
      type: { type: 'string', enum: ['feat', 'fix', 'chore', ...] },
      scope: { type: 'string', nullable: true },
      is_breaking: { type: 'boolean' },
      is_internal: { type: 'boolean' },
      confidence: { type: 'number', minimum: 0, maximum: 1 },
      user_impact_summary: { type: 'string' },
      developer_summary: { type: 'string' }
    },
    required: ['type', 'is_breaking', 'is_internal', 'confidence', 'user_impact_summary', 'developer_summary']
  }
};
```

Prompt caching: use Anthropic's prompt caching for the system prompt (which is identical across all classifications in a batch). Cache breakpoints placed after the system prompt.

**Testing**:
- `test-prompt-includes-all-types`: System prompt lists all CommitType values
- `test-prompt-context-enrichment`: PR title and body included when available
- `test-prompt-diff-stats-included`: File paths and change counts included for context
- `test-tool-schema-valid`: Tool definition validates against Anthropic API schema
- `test-prompt-cache-breakpoint`: System prompt marked with cache_control

#### 3.3 — Ollama Local LLM Provider
**What**: Implement the LLM provider interface for Ollama, enabling local/private classification.

**Design**:
```typescript
// src/classifier/ollama-classifier.ts

export class OllamaClassifier implements LLMProvider {
  readonly name = 'ollama';
  constructor(baseUrl: string, model: string);  // default: http://localhost:11434, llama3.2
  async classify(input: ClassificationInput): Promise<ClassificationOutput>;
  async classifyBatch(inputs: ClassificationInput[], batchSize?: number): Promise<ClassificationOutput[]>;
}
```

Ollama does not support tool_use; use JSON mode with a schema constraint in the prompt. Lower default confidence threshold (0.6 vs 0.7) for local models due to expected lower accuracy.

**Testing**:
- `test-ollama-json-output`: Response parsed from JSON mode output
- `test-ollama-connection-error`: Clear error message when Ollama is not running
- `test-ollama-model-not-found`: Helpful error when specified model is not pulled
- `test-ollama-batch-sequential`: Batches processed sequentially (Ollama is single-threaded)

#### 3.4 — Hybrid Classification Pipeline
**What**: Wire the full classification pipeline: Conventional Commits first, AI fallback for non-matching, confidence-based flagging.

**Design**:
```typescript
// Updated src/classifier/index.ts

export class CommitClassifier {
  constructor(
    config: ChangelogGenConfig['classification'],
    llmProvider: LLMProvider | null
  );

  async classifyAll(commits: CommitInfo[]): Promise<ClassifiedCommit[]> {
    const filtered = this.filterCommits(commits);
    const results: ClassifiedCommit[] = [];

    // Phase 1: Try Conventional Commits parser
    const unclassified: CommitInfo[] = [];
    for (const commit of filtered) {
      const cc = classifyConventional(commit);
      if (cc) {
        results.push({ commit, classification: cc, isFiltered: false });
      } else {
        unclassified.push(commit);
      }
    }

    // Phase 2: AI classification for remaining commits
    if (unclassified.length > 0 && this.llmProvider) {
      const aiResults = await this.llmProvider.classifyBatch(
        unclassified.map(c => this.buildClassificationInput(c))
      );
      // merge results...
    }

    // Phase 3: Flag low-confidence classifications
    for (const result of results) {
      if (result.classification?.confidence &&
          result.classification.confidence < this.config.confidenceThreshold) {
        result.needsReview = true;
      }
    }

    return results;
  }
}
```

**Testing**:
- `test-hybrid-cc-takes-priority`: CC-formatted commit classified by parser even when AI is available
- `test-hybrid-ai-fallback`: Non-CC commit classified by AI when available
- `test-hybrid-no-ai-graceful`: Without AI provider, non-CC commits returned unclassified with warning
- `test-low-confidence-flagged`: Classification at 0.55 flagged for review (threshold 0.7)
- `test-mixed-repo`: Repo with 60% CC and 40% free-text commits processed correctly

---

## Phase 4: Changelog Entry Generation & Audience Variants

### Purpose
Transform classified commits into polished changelog entries with dual-audience output (developer CHANGELOG and user-facing "What's New"). This delivers the primary value proposition.

### Tasks

#### 4.1 — Entry Builder
**What**: Group classified commits by category and generate changelog entries, merging related commits into single entries where appropriate.

**Design**:
```typescript
// src/generator/entry-builder.ts

export class EntryBuilder {
  constructor(private config: ChangelogGenConfig['output']);

  /**
   * Build changelog entries from classified commits.
   * Groups commits by category (Keep a Changelog v1.1.0).
   * Merges commits that share the same scope or PR.
   * Filters internal commits (refactor, chore, ci, build, test) from non-developer audiences.
   */
  build(classifiedCommits: ClassifiedCommit[]): ChangelogEntry[];

  /**
   * Merge related commits into a single entry.
   * Criteria: same PR, same scope+type, or AI-determined relatedness.
   */
  private mergeRelated(commits: ClassifiedCommit[]): CommitGroup[];
}

interface CommitGroup {
  commits: ClassifiedCommit[];
  category: ChangelogCategory;
  scope: string | null;
  isBreaking: boolean;
}
```

**Testing**:
- `test-group-by-category`: feat->Added, fix->Fixed, perf->Changed
- `test-filter-internal-commits`: refactor/chore/ci/test/build commits excluded from entries
- `test-merge-same-pr`: Three commits from PR #42 merged into one entry
- `test-merge-same-scope`: Two `fix(parser)` commits merged into one "Fixed" entry
- `test-breaking-changes-highlighted`: Breaking changes get `BREAKING` prefix
- `test-single-commit-entry`: One-commit-per-entry when no merging criteria match

#### 4.2 — Audience-Aware Content Writer
**What**: Generate audience-specific variants of each changelog entry using LLM, producing developer-technical and user-benefit text from the same source.

**Design**:
```typescript
// src/generator/audience-writer.ts

export class AudienceWriter {
  constructor(private llmProvider: LLMProvider);

  /**
   * Generate audience variants for a batch of entries.
   * Developer variant: technical details (API changes, method names, config keys)
   * End-user variant: benefit statements (what's new, what's fixed, what's improved)
   * Admin variant: operational notes (env vars, performance impact, security patches)
   */
  async generateVariants(
    entries: ChangelogEntry[],
    audiences: Audience[]
  ): Promise<Map<string, Record<Audience, AudienceVariant>>>;
}

// LLM prompt structure for audience writing:
// "Given this technical changelog entry and its source commit context,
//  rewrite it for the following audience: {audience}.
//  Developer: focus on API changes, technical details, code-level impact.
//  End user: focus on benefits, problems solved, new capabilities. Omit internal details.
//  Admin: focus on deployment impact, configuration changes, security patches, performance."
```

**Testing**:
- `test-developer-variant-technical`: Developer variant includes API method names and config keys
- `test-user-variant-benefit-focused`: User variant uses benefit language ("You can now...")
- `test-admin-variant-operational`: Admin variant mentions env vars, performance, security
- `test-internal-filtered-for-users`: Refactor entries produce `is_visible: false` for end_user audience
- `test-security-visible-to-all`: Security entries visible to all audiences
- `test-breaking-change-emphasized`: Breaking changes prominently noted in all variants
- `test-batch-generation`: 20 entries with 3 audiences = 60 variants generated efficiently

#### 4.3 — Version Calculator
**What**: Calculate the next SemVer version based on the classified changes in the release.

**Design**:
```typescript
// src/generator/version-calculator.ts

export class VersionCalculator {
  /**
   * Calculate the next version based on classified commits.
   * Rules (SemVer 2.0.0):
   *   - Any breaking change -> MAJOR bump
   *   - Any feat -> MINOR bump
   *   - Only fixes/patches -> PATCH bump
   *   - No relevant changes -> no bump (returns null)
   */
  calculate(
    currentVersion: SemanticVersion,
    entries: ChangelogEntry[]
  ): { nextVersion: SemanticVersion; bumpType: 'major' | 'minor' | 'patch'; reason: string } | null;

  /**
   * Parse a version string into SemanticVersion.
   * Supports both "v1.2.3" and "1.2.3" formats.
   */
  static parse(versionString: string): SemanticVersion;

  /**
   * Format a SemanticVersion back to string.
   * Produces "1.2.3" format (without "v" prefix).
   */
  static format(version: SemanticVersion): string;
}
```

**Testing**:
- `test-breaking-bumps-major`: Breaking change in entries -> MAJOR bump
- `test-feat-bumps-minor`: Feature with no breaking -> MINOR bump
- `test-fix-only-bumps-patch`: Only fixes -> PATCH bump
- `test-no-relevant-changes`: Only internal changes -> null (no bump)
- `test-prerelease-handling`: Current "1.2.3-alpha.1" + feat -> "1.3.0" (drops prerelease)
- `test-parse-v-prefix`: "v1.2.3" parsed correctly, "v" stripped
- `test-parse-calver`: "2026.05.11" parsed as CalVer with appropriate scheme

#### 4.4 — Generate Command End-to-End
**What**: Wire the full `changelog-gen generate` pipeline: git -> classify -> build entries -> render output.

**Design**:
```typescript
// src/cli/commands/generate.ts

export async function generateCommand(options: GenerateOptions): Promise<void> {
  // 1. Load config
  const config = loadConfig(options.config);

  // 2. Open git repository
  const repo = new GitRepository(process.cwd());

  // 3. Resolve commit range
  const since = options.since ?? (await repo.getLatestTag())?.name ?? null;
  const until = options.until ?? 'HEAD';

  // 4. Get commits
  const commits = await repo.getCommits(since, until);

  // 5. Classify commits
  const classifier = new CommitClassifier(config.classification, llmProvider);
  const classified = await classifier.classifyAll(commits);

  // 6. Build entries
  const builder = new EntryBuilder(config.output);
  const entries = builder.build(classified);

  // 7. Generate audience variants (if multiple audiences configured)
  if (config.output.audiences.length > 1) {
    const writer = new AudienceWriter(llmProvider);
    const variants = await writer.generateVariants(entries, config.output.audiences);
    // merge variants into entries...
  }

  // 8. Calculate version
  const currentVersion = VersionCalculator.parse(since ?? '0.0.0');
  const versionResult = new VersionCalculator().calculate(currentVersion, entries);

  // 9. Render output
  const renderer = new MarkdownRenderer(handlebars);
  const release: ReleaseInfo = { /* assemble from above */ };
  const output = renderer.render(release, renderOptions);

  // 10. Write or print
  if (options.dryRun) {
    console.log(output);
  } else {
    fs.writeFileSync(options.output ?? 'CHANGELOG.md', output);
  }
}
```

**Testing**:
- `test-e2e-generate-from-tags`: Full pipeline from tag range to CHANGELOG.md output
- `test-e2e-dry-run`: `--dry-run` prints to stdout without creating files
- `test-e2e-dual-audience`: `--audience developer,end_user` produces two output files
- `test-e2e-no-tags`: Repository with no tags generates from first commit
- `test-e2e-empty-range`: No changes between refs produces "No changes" message
- `test-e2e-mixed-commits`: Mix of CC and free-text commits classified and rendered correctly

---

## Phase 5: GitHub & GitLab Integration

### Purpose
Integrate with GitHub and GitLab APIs to fetch PR metadata, create releases, and enable the GitHub Action distribution model.

### Tasks

#### 5.1 — GitHub Provider
**What**: Implement GitHub API integration for fetching PRs, issues, and creating releases.

**Design**:
```typescript
// src/providers/github.ts
import { Octokit } from '@octokit/rest';

export class GitHubProvider {
  private octokit: Octokit;

  constructor(token: string, owner: string, repo: string);

  /** Fetch merged PRs in a commit range */
  async getPullRequests(commitShas: string[]): Promise<SourceItem[]>;

  /** Fetch issues referenced in commits or PRs */
  async getIssues(issueNumbers: number[]): Promise<SourceItem[]>;

  /** Create or update a GitHub Release */
  async createRelease(params: {
    tagName: string;
    name: string;
    body: string;
    draft: boolean;
    prerelease: boolean;
  }): Promise<{ id: number; url: string }>;

  /** Fetch PR body and labels for enriched classification context */
  async enrichCommitContext(commitSha: string): Promise<{
    prTitle: string | null;
    prBody: string | null;
    labels: string[];
  }>;
}
```

Authentication: support `GITHUB_TOKEN` (Actions), personal access tokens, and GitHub App installation tokens. Pagination: auto-paginate using Octokit's built-in iterator. Rate limiting: monitor `X-RateLimit-Remaining` header and pause when approaching limits.

**Testing**:
- `test-fetch-prs-for-commits`: Map commit SHAs to their associated merged PRs
- `test-fetch-issues`: Fetch issue titles and bodies by number
- `test-create-release`: Create a GitHub Release with markdown body
- `test-enrich-commit-context`: Commit SHA mapped to PR title, body, and labels
- `test-pagination`: Repos with >100 PRs paginated correctly
- `test-rate-limit-handling`: 403 rate limit response triggers wait and retry
- `test-github-app-auth`: Installation token authentication works

#### 5.2 — GitLab Provider
**What**: Implement GitLab API integration for merge requests, issues, and releases.

**Design**:
```typescript
// src/providers/gitlab.ts
import { Gitlab } from '@gitbeaker/rest';

export class GitLabProvider {
  private gitlab: InstanceType<typeof Gitlab>;

  constructor(token: string, projectId: string | number, apiUrl?: string);

  async getMergeRequests(commitShas: string[]): Promise<SourceItem[]>;
  async getIssues(issueIds: number[]): Promise<SourceItem[]>;
  async createRelease(params: {
    tagName: string;
    description: string;
  }): Promise<{ id: number; url: string }>;
  async enrichCommitContext(commitSha: string): Promise<{
    mrTitle: string | null;
    mrBody: string | null;
    labels: string[];
  }>;
}
```

Support both GitLab.com and self-hosted instances via `apiUrl` parameter.

**Testing**:
- `test-gitlab-merge-requests`: Fetch MRs associated with commits
- `test-gitlab-create-release`: Create release with tag and description
- `test-gitlab-self-hosted`: Self-hosted instance with custom API URL
- `test-gitlab-job-token-auth`: CI_JOB_TOKEN authentication in GitLab CI

#### 5.3 — Provider Registry & Context Enrichment
**What**: Create a provider registry that auto-detects the VCS provider from git remote URL and enriches commit classification with PR/issue context.

**Design**:
```typescript
// src/providers/index.ts

export class ProviderRegistry {
  private providers: Map<string, GitHubProvider | GitLabProvider>;

  /** Auto-detect provider from git remote URL */
  static detectProvider(remoteUrl: string): VCSProvider;

  /** Get the configured provider for this repository */
  getProvider(): GitHubProvider | GitLabProvider | null;

  /**
   * Enrich commits with PR and issue context before classification.
   * Fetches PR titles, bodies, and labels for each commit.
   * Extracts issue references (e.g., "Fixes #123", "MYAPP-456") from messages and PR bodies.
   */
  async enrichCommits(commits: CommitInfo[]): Promise<EnrichedCommit[]>;
}

export interface EnrichedCommit extends CommitInfo {
  pullRequest: SourceItem | null;
  linkedIssues: SourceItem[];
}
```

**Testing**:
- `test-detect-github`: `"git@github.com:org/repo.git"` detected as github
- `test-detect-gitlab`: `"https://gitlab.com/org/repo.git"` detected as gitlab
- `test-enrich-with-pr`: Commit enriched with PR title, body, and labels
- `test-extract-issue-refs`: `"Fixes #123"` and `"MYAPP-456"` extracted from commit message
- `test-no-provider-graceful`: Local-only repo operates without provider (no enrichment)

#### 5.4 — GitHub Action
**What**: Create the GitHub Action entry point (`action.yml`) for use in CI/CD workflows.

**Design**:
```yaml
# action.yml
name: 'Changelog Generator'
description: 'AI-powered changelog and release notes from git history'
inputs:
  since:
    description: 'Start ref (tag, SHA). Default: latest tag'
    required: false
  until:
    description: 'End ref. Default: HEAD'
    required: false
    default: 'HEAD'
  output-file:
    description: 'Output file path'
    required: false
    default: 'CHANGELOG.md'
  audience:
    description: 'Target audience(s), comma-separated'
    required: false
    default: 'developer'
  create-release:
    description: 'Create a GitHub Release'
    required: false
    default: 'false'
  anthropic-api-key:
    description: 'Anthropic API key for AI classification'
    required: false
outputs:
  version:
    description: 'Calculated next version'
  changelog:
    description: 'Generated changelog content'
  release-url:
    description: 'URL of created GitHub Release (if create-release is true)'
runs:
  using: 'node20'
  main: 'dist/action/index.js'
```

**Testing**:
- `test-action-inputs-parsed`: All inputs correctly mapped to config
- `test-action-creates-release`: `create-release: true` triggers GitHub Release creation
- `test-action-outputs-set`: `version` and `changelog` outputs populated
- `test-action-without-api-key`: Runs with CC-only classification when no API key provided
- `test-action-shallow-clone`: Works with `fetch-depth: 0` and warns without it

---

## Phase 6: Issue Tracker Integration (Jira & Linear)

### Purpose
Fetch business context from Jira and Linear issue trackers to produce release notes that reflect why changes matter, not just what changed technically.

### Tasks

#### 6.1 — Jira Provider
**What**: Integrate with Jira REST v3 API to fetch issue details for referenced tickets.

**Design**:
```typescript
// src/providers/jira.ts
import { Version3Client } from 'jira.js';

export class JiraProvider {
  private client: Version3Client;

  constructor(config: {
    apiBaseUrl: string;     // e.g. "https://company.atlassian.net"
    email: string;
    token: string;
    projectKey: string;
  });

  /** Fetch issue by key (e.g., "MYAPP-789") */
  async getIssue(issueKey: string): Promise<SourceItem>;

  /** Fetch all issues linked to a fixVersion */
  async getIssuesByVersion(versionName: string): Promise<SourceItem[]>;

  /** Extract issue keys from text using project-key pattern */
  extractIssueKeys(text: string): string[];

  /** Build SourceItem from Jira issue response */
  private mapToSourceItem(issue: JiraIssue): SourceItem;
  // metadata includes: issue_type, priority, fix_version, epic_key, acceptance_criteria, labels
}
```

Issue key extraction regex: `/\b{projectKey}-\d+\b/g` where `{projectKey}` comes from config. Handles both Cloud and Server APIs (Cloud uses v3, Server uses v2).

**Testing**:
- `test-fetch-jira-issue`: Issue key "MYAPP-789" returns title, body, type, priority
- `test-extract-keys-from-commit`: `"Fixes MYAPP-789 and MYAPP-790"` extracts both keys
- `test-extract-keys-from-pr-body`: Keys extracted from PR description text
- `test-issue-by-version`: All issues with fixVersion "1.3.0" retrieved
- `test-acceptance-criteria-captured`: Jira acceptance criteria field included in metadata
- `test-auth-basic`: Email + API token authentication works
- `test-jira-cloud-vs-server`: Cloud (v3) and Server (v2) API paths handled

#### 6.2 — Linear Provider
**What**: Integrate with Linear's GraphQL API to fetch issue details.

**Design**:
```typescript
// src/providers/linear.ts
import { LinearClient } from '@linear/sdk';

export class LinearProvider {
  private client: LinearClient;

  constructor(apiKey: string, teamKey?: string);

  /** Fetch issue by identifier (e.g., "ENG-123") */
  async getIssue(identifier: string): Promise<SourceItem>;

  /** Fetch issues for a project or cycle */
  async getIssuesByProject(projectName: string): Promise<SourceItem[]>;

  /** Extract Linear identifiers from text */
  extractIdentifiers(text: string): string[];
  // Pattern: /\b[A-Z]{2,5}-\d+\b/g
}
```

**Testing**:
- `test-fetch-linear-issue`: "ENG-123" returns title, body, state, priority
- `test-extract-identifiers`: `"Closes ENG-123"` extracts identifier
- `test-issues-by-project`: All issues in "Auth Improvements" project retrieved
- `test-graphql-rate-limit`: 1500 req/hr limit respected with backoff

#### 6.3 — Context-Enriched Entry Generation
**What**: Enhance the entry builder to incorporate issue tracker context into changelog entries.

**Design**:
```typescript
// Updated src/generator/entry-builder.ts

export class EntryBuilder {
  /**
   * Build entries with issue context.
   * When an issue is linked:
   *   1. Use issue title as the primary description (it's user-language)
   *   2. Include issue body/acceptance criteria in LLM prompt for better audience writing
   *   3. Attribute entries to business features (epics, projects)
   *   4. Link to issue URL in output
   */
  buildWithContext(
    classifiedCommits: ClassifiedCommit[],
    issueContext: Map<string, SourceItem>
  ): ChangelogEntry[];
}
```

The LLM prompt for audience-variant generation now includes:
- Commit message + diff stats (code context)
- PR title + body (developer context)
- Issue title + body + acceptance criteria (business context)

This enables the LLM to generate user-facing notes like "You can now log in with your company credentials" instead of "Implement OIDC auth flow" because it has the Jira story context.

**Testing**:
- `test-issue-title-in-entry`: Entry uses Jira issue title when available
- `test-acceptance-criteria-improves-user-variant`: User variant references acceptance criteria language
- `test-epic-attribution`: Entries grouped by epic when configured
- `test-no-issue-fallback`: Commits without linked issues use commit/PR context only
- `test-multiple-providers`: Same commit linked to both GitHub Issue and Jira ticket

---

## Phase 7: Database & Persistence Layer

### Purpose
Add PostgreSQL persistence so that classification results, releases, and entries are stored, enabling incremental updates, re-rendering, and audit trails.

### Tasks

#### 7.1 — Database Schema (Drizzle ORM)
**What**: Define the database schema using Drizzle ORM, implementing the Hybrid Relational + JSONB model (Data Model Suggestion 3).

**Design**:
```typescript
// src/db/schema.ts
import { pgTable, uuid, text, boolean, integer, date, timestamp, jsonb, uniqueIndex, index } from 'drizzle-orm/pg-core';

export const repositories = pgTable('repositories', {
  id: uuid('id').primaryKey().defaultRandom(),
  name: text('name').notNull(),
  provider: text('provider').notNull(),  // 'github' | 'gitlab' | 'bitbucket' | 'local'
  defaultBranch: text('default_branch').notNull().default('main'),
  isMonorepo: boolean('is_monorepo').notNull().default(false),
  providerConfig: jsonb('provider_config').notNull().default({}),
  issueTrackers: jsonb('issue_trackers').notNull().default([]),
  generatorConfig: jsonb('generator_config').notNull().default({}),
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => ({
  providerNameUnique: uniqueIndex().on(table.provider, table.name),
}));

export const commits = pgTable('commits', {
  id: uuid('id').primaryKey().defaultRandom(),
  repositoryId: uuid('repository_id').notNull().references(() => repositories.id, { onDelete: 'cascade' }),
  sha: text('sha').notNull(),
  messageSubject: text('message_subject').notNull(),
  messageBody: text('message_body'),
  committedAt: timestamp('committed_at', { withTimezone: true }).notNull(),
  isMergeCommit: boolean('is_merge_commit').notNull().default(false),
  authorInfo: jsonb('author_info').notNull().default({}),
  diffStats: jsonb('diff_stats'),
  classification: jsonb('classification'),
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => ({
  repoShaUnique: uniqueIndex().on(table.repositoryId, table.sha),
  repoDateIdx: index().on(table.repositoryId, table.committedAt),
}));

export const sourceItems = pgTable('source_items', {
  id: uuid('id').primaryKey().defaultRandom(),
  repositoryId: uuid('repository_id').notNull().references(() => repositories.id, { onDelete: 'cascade' }),
  itemType: text('item_type').notNull(),  // 'pull_request' | 'issue' | 'ticket'
  provider: text('provider').notNull(),
  providerItemId: text('provider_item_id').notNull(),
  title: text('title').notNull(),
  body: text('body'),
  status: text('status').notNull(),
  authorInfo: jsonb('author_info').notNull().default({}),
  metadata: jsonb('metadata').notNull().default({}),
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => ({
  providerItemUnique: uniqueIndex().on(table.repositoryId, table.provider, table.itemType, table.providerItemId),
}));

export const commitSourceLinks = pgTable('commit_source_links', {
  id: uuid('id').primaryKey().defaultRandom(),
  commitId: uuid('commit_id').notNull().references(() => commits.id, { onDelete: 'cascade' }),
  sourceItemId: uuid('source_item_id').notNull().references(() => sourceItems.id, { onDelete: 'cascade' }),
  linkType: text('link_type').notNull(),  // 'authored_in' | 'fixes' | 'references' | 'closes'
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
});

export const releases = pgTable('releases', {
  id: uuid('id').primaryKey().defaultRandom(),
  repositoryId: uuid('repository_id').notNull().references(() => repositories.id, { onDelete: 'cascade' }),
  packageId: uuid('package_id'),
  tagName: text('tag_name').notNull(),
  version: jsonb('version').notNull(),
  releaseDate: date('release_date').notNull(),
  title: text('title'),
  status: text('status').notNull().default('draft'),
  isPrerelease: boolean('is_prerelease').notNull().default(false),
  commitRange: jsonb('commit_range').notNull(),
  versionDecision: jsonb('version_decision'),
  publications: jsonb('publications').notNull().default([]),
  stats: jsonb('stats').notNull().default({}),
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => ({
  repoTagUnique: uniqueIndex().on(table.repositoryId, table.tagName),
}));

export const changelogEntries = pgTable('changelog_entries', {
  id: uuid('id').primaryKey().defaultRandom(),
  releaseId: uuid('release_id').notNull().references(() => releases.id, { onDelete: 'cascade' }),
  category: text('category').notNull(),
  bodyMarkdown: text('body_markdown').notNull(),
  displayOrder: integer('display_order').notNull().default(0),
  isBreaking: boolean('is_breaking').notNull().default(false),
  isSecurity: boolean('is_security').notNull().default(false),
  isHighlight: boolean('is_highlight').notNull().default(false),
  sources: jsonb('sources').notNull().default({}),
  generation: jsonb('generation').notNull().default({}),
  audienceVariants: jsonb('audience_variants').notNull().default({}),
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
});

export const templates = pgTable('templates', {
  id: uuid('id').primaryKey().defaultRandom(),
  repositoryId: uuid('repository_id'),
  name: text('name').notNull(),
  audience: text('audience'),
  format: text('format').notNull(),
  templateBody: text('template_body').notNull(),
  templateConfig: jsonb('template_config').notNull().default({}),
  isDefault: boolean('is_default').notNull().default(false),
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
});

export const renderedCache = pgTable('rendered_cache', {
  id: uuid('id').primaryKey().defaultRandom(),
  releaseId: uuid('release_id').notNull().references(() => releases.id, { onDelete: 'cascade' }),
  audience: text('audience'),
  format: text('format').notNull(),
  content: text('content').notNull(),
  contentHash: text('content_hash').notNull(),
  templateId: uuid('template_id'),
  renderedAt: timestamp('rendered_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => ({
  releaseAudienceFormatUnique: uniqueIndex().on(table.releaseId, table.audience, table.format),
}));

export const auditLog = pgTable('audit_log', {
  id: uuid('id').primaryKey().defaultRandom(),
  repositoryId: uuid('repository_id'),
  releaseId: uuid('release_id'),
  action: text('action').notNull(),
  actor: text('actor'),
  details: jsonb('details').notNull().default({}),
  occurredAt: timestamp('occurred_at', { withTimezone: true }).notNull().defaultNow(),
});
```

**Testing**:
- `test-migration-creates-tables`: Migration creates all 8 tables
- `test-migration-rollback`: Rollback drops tables cleanly
- `test-unique-constraints`: Duplicate repo/sha pair rejected
- `test-cascade-delete`: Deleting a repository cascades to commits, releases, entries
- `test-jsonb-query`: `classification @> '{"type": "feat"}'` query returns matching commits

#### 7.2 — Repository & Commit Persistence
**What**: Implement data access layer for storing and retrieving repositories and commits.

**Design**:
```typescript
// src/db/queries.ts

export class ChangelogDB {
  constructor(private db: DrizzleInstance);

  // Repository operations
  async upsertRepository(repo: NewRepository): Promise<Repository>;
  async getRepository(provider: string, name: string): Promise<Repository | null>;

  // Commit operations
  async upsertCommits(repositoryId: string, commits: CommitInfo[]): Promise<void>;
  async getCommitsBySha(repositoryId: string, shas: string[]): Promise<Commit[]>;
  async getUnclassifiedCommits(repositoryId: string): Promise<Commit[]>;
  async updateClassification(commitId: string, classification: CommitClassification): Promise<void>;

  // Release operations
  async createRelease(release: NewRelease): Promise<Release>;
  async getReleases(repositoryId: string, limit?: number): Promise<Release[]>;
  async updateReleaseStatus(releaseId: string, status: ReleaseStatus): Promise<void>;

  // Entry operations
  async createEntries(releaseId: string, entries: ChangelogEntry[]): Promise<void>;
  async getEntriesByRelease(releaseId: string): Promise<ChangelogEntry[]>;

  // Audit operations
  async logAction(action: string, details: Record<string, unknown>): Promise<void>;
}
```

**Testing**:
- `test-upsert-commits-idempotent`: Re-ingesting same commits does not create duplicates
- `test-classification-update-preserves-history`: Previous classification stored in JSONB array
- `test-get-unclassified`: Only commits with null classification returned
- `test-audit-log-appended`: Each operation creates an audit log entry
- `test-db-connection-error-handling`: Clear error when PostgreSQL is unavailable

#### 7.3 — Incremental Pipeline
**What**: Modify the generate pipeline to use the database for incremental updates.

**Design**:
```typescript
// Updated generate pipeline:
// 1. Ingest new commits into DB (upsert — skip already-stored commits)
// 2. Classify only unclassified commits (skip previously classified)
// 3. Create release record with entries
// 4. Render from DB (cache in rendered_cache table)
// 5. Publish and update publication status

// New CLI flag: --persist (default: false for CLI, true for CI/CD)
// Without --persist: operates in-memory only (no DB required)
// With --persist: stores to PostgreSQL and enables incremental updates
```

**Testing**:
- `test-incremental-skips-classified`: Previously classified commits not re-sent to AI
- `test-incremental-new-commits-only`: Only commits since last run are ingested
- `test-no-persist-mode`: CLI works without database (in-memory mode)
- `test-persist-mode-stores`: With `--persist`, data written to PostgreSQL
- `test-re-render-from-db`: Existing release re-rendered from stored entries

---

## Phase 8: Output Renderers & Templates

### Purpose
Implement all output formats (HTML, JSON, Atom feed) and the Handlebars template system for user-customizable output.

### Tasks

#### 8.1 — HTML Renderer
**What**: Render changelog as HTML with semantic markup and optional CSS styling.

**Design**:
```typescript
// src/renderer/html.ts

export class HtmlRenderer {
  render(release: ReleaseInfo, options: RenderOptions): string;
  renderFull(releases: ReleaseInfo[], unreleased: ChangelogEntry[]): string;
}

// Output: semantic HTML with <article>, <section>, <h2>-<h3>, <ul>/<li>
// Classes: .changelog, .release, .category, .entry, .breaking, .security
// Inline CSS option for email-compatible rendering
```

**Testing**:
- `test-html-valid-markup`: Output passes HTML5 validation
- `test-html-semantic-elements`: Uses `<article>`, `<section>`, `<time>`
- `test-html-breaking-class`: Breaking changes have `.breaking` class
- `test-html-inline-css`: Inline CSS mode for email rendering

#### 8.2 — JSON Renderer
**What**: Render changelog as structured JSON for programmatic consumption.

**Design**:
```typescript
// src/renderer/json.ts

export class JsonRenderer {
  render(release: ReleaseInfo): ChangelogJson;
  renderFull(releases: ReleaseInfo[]): ChangelogJson;
}

interface ChangelogJson {
  $schema: string;            // URL to JSON Schema
  generatedAt: string;        // ISO 8601
  generator: string;          // "changelog-gen@1.0.0"
  releases: Array<{
    version: string;
    date: string;
    categories: Record<ChangelogCategory, Array<{
      text: string;
      isBreaking: boolean;
      sources: { commits: string[]; pullRequests: string[]; issues: string[] };
      audienceVariants?: Record<Audience, string>;
    }>>;
  }>;
}
```

Publish JSON Schema at `changelog-gen.schema.json` for consumer validation (per JSON Schema Draft 2020-12 standard).

**Testing**:
- `test-json-valid-schema`: Output validates against published JSON Schema
- `test-json-audience-variants`: Variants included when requested
- `test-json-sources-populated`: Commit SHAs, PR numbers, issue IDs present
- `test-json-iso-dates`: All dates in ISO 8601 format

#### 8.3 — Atom Feed Renderer
**What**: Render changelog as an Atom feed (RFC 4287) for subscription-based changelog delivery.

**Design**:
```typescript
// src/renderer/atom.ts

export class AtomRenderer {
  render(releases: ReleaseInfo[], feedMeta: AtomFeedMeta): string;
}

interface AtomFeedMeta {
  title: string;              // e.g. "my-org/my-repo Releases"
  feedUrl: string;            // self-link
  siteUrl: string;            // alternate link
  authorName: string;
}

// Output: valid Atom XML per RFC 4287
// Each release = one <entry> with:
//   <id>: tag URI (tag:github.com,2026:my-org/my-repo/v1.3.0)
//   <title>: version + title
//   <updated>: release date ISO 8601
//   <content type="html">: rendered HTML changelog
//   <link rel="alternate">: URL to GitHub/GitLab release
```

**Testing**:
- `test-atom-valid-xml`: Output is well-formed XML
- `test-atom-rfc4287-compliant`: Required Atom elements present (id, title, updated, author)
- `test-atom-entry-per-release`: Each release is a separate `<entry>`
- `test-atom-html-content`: Entry content is HTML-rendered changelog

#### 8.4 — Custom Template System
**What**: Implement Handlebars-based template customization with built-in templates and user-override support.

**Design**:
```typescript
// src/renderer/index.ts

export class TemplateEngine {
  constructor();

  /** Register built-in templates */
  registerBuiltins(): void;

  /** Load user templates from filesystem */
  loadUserTemplates(dir: string): void;

  /** Render using a named template */
  render(templateName: string, data: TemplateData): string;
}

// Built-in templates:
// - "default": Keep a Changelog v1.1.0 format
// - "user-facing": "What's New" format with benefit-focused language
// - "compact": Single-line-per-entry for Slack/email
// - "github-release": GitHub Releases markdown format

// Handlebars helpers:
// {{formatDate date "YYYY-MM-DD"}}
// {{#ifBreaking}}...{{/ifBreaking}}
// {{#eachCategory entries}}...{{/eachCategory}}
// {{audienceText entry "end_user"}}
// {{commitLink sha provider}}
// {{issueLink id provider}}
```

**Testing**:
- `test-default-template-kac-format`: Default template matches Keep a Changelog v1.1.0
- `test-user-template-override`: User template in `./templates/` takes precedence
- `test-handlebars-helpers`: All custom helpers produce correct output
- `test-missing-template-error`: Referencing nonexistent template produces clear error
- `test-template-data-complete`: All expected variables available in template context

---

## Phase 9: Publishing & Distribution

### Purpose
Enable automated publishing of generated changelogs to multiple channels: GitHub/GitLab Releases, CHANGELOG.md file commits, Slack notifications.

### Tasks

#### 9.1 — File Publisher
**What**: Write rendered changelog to CHANGELOG.md with intelligent merge (prepend new release, preserve existing content).

**Design**:
```typescript
// src/publisher/file-writer.ts

export class FilePublisher {
  /**
   * Write changelog to file.
   * If file exists: parse existing releases, prepend new release, preserve old content.
   * If file doesn't exist: create with full header per Keep a Changelog v1.1.0.
   * Update [Unreleased] link to point to new comparison URL.
   */
  async publish(params: {
    filePath: string;
    release: ReleaseInfo;
    renderedContent: string;
    fullChangelog?: string;
  }): Promise<void>;

  /**
   * Parse existing CHANGELOG.md to extract release boundaries.
   * Used for intelligent merging without duplicating releases.
   */
  parseExisting(filePath: string): ExistingChangelog;
}
```

**Testing**:
- `test-create-new-changelog`: New file created with KaC header
- `test-prepend-to-existing`: New release prepended; old releases preserved
- `test-no-duplicate-release`: Re-running for same version doesn't duplicate
- `test-unreleased-section-updated`: [Unreleased] comparison URL updated
- `test-preserves-manual-edits`: Manually added content in existing releases preserved

#### 9.2 — GitHub/GitLab Release Publisher
**What**: Create or update platform releases with generated changelog content.

**Design**:
```typescript
// src/publisher/github-release.ts

export class GitHubReleasePublisher {
  async publish(params: {
    tagName: string;
    title: string;
    body: string;
    draft: boolean;
    prerelease: boolean;
    audience: Audience;
  }): Promise<{ url: string }>;
}

// src/publisher/gitlab-release.ts
export class GitLabReleasePublisher {
  async publish(params: {
    tagName: string;
    description: string;
  }): Promise<{ url: string }>;
}
```

**Testing**:
- `test-github-release-created`: Release created with correct tag, title, and body
- `test-github-release-updated`: Existing release updated (not duplicated)
- `test-gitlab-release-created`: GitLab release with markdown description
- `test-draft-release`: Draft release not publicly visible
- `test-audience-specific-release`: Different body content based on audience

#### 9.3 — Slack Publisher
**What**: Post release notes to Slack via webhook.

**Design**:
```typescript
// src/publisher/slack.ts

export class SlackPublisher {
  async publish(params: {
    webhookUrl: string;
    release: ReleaseInfo;
    renderedContent: string;
    channel?: string;
  }): Promise<void>;
}

// Slack Block Kit format:
// - Header block: version + date
// - Section block per category with mrkdwn formatting
// - Context block: contributor list
// - Divider between categories
// Truncate to Slack's 3000-char block limit; link to full changelog
```

**Testing**:
- `test-slack-webhook-post`: POST to webhook URL with Block Kit payload
- `test-slack-truncation`: Long changelogs truncated with "Read more" link
- `test-slack-formatting`: Markdown converted to Slack mrkdwn syntax
- `test-slack-error-handling`: 4xx/5xx responses produce clear error messages

#### 9.4 — Publish Command & Multi-Channel Orchestration
**What**: Implement the `changelog-gen publish` command that distributes to multiple channels.

**Design**:
```typescript
// src/cli/commands/publish.ts

export async function publishCommand(options: PublishOptions): Promise<void> {
  // 1. Load the latest release from DB (or generate in-memory)
  // 2. Render for each configured channel and audience
  // 3. Publish to all channels in parallel
  // 4. Update publication status in DB
  // 5. Log to audit trail
}

// CLI: changelog-gen publish --channels github,slack,file --audience developer,end_user
```

**Testing**:
- `test-publish-multi-channel`: Single command publishes to GitHub + Slack + file
- `test-publish-partial-failure`: Slack failure doesn't block GitHub release
- `test-publish-idempotent`: Re-publishing to same channel updates, not duplicates
- `test-publish-records-status`: Publication status stored in DB with timestamps

---

## Phase 10: Monorepo Support

### Purpose
Support monorepo workflows with independent per-package versioning and changelogs, aligning with changesets and release-please patterns.

### Tasks

#### 10.1 — Package Detection & Scoping
**What**: Detect packages in a monorepo and scope commits to affected packages based on file paths.

**Design**:
```typescript
// src/git/monorepo.ts

export class MonorepoAnalyzer {
  constructor(private packages: PackageConfig[]);

  /** Detect packages from workspace config (package.json workspaces, pnpm-workspace.yaml) */
  static detectPackages(workingDir: string): PackageConfig[];

  /** Scope a commit to one or more packages based on changed file paths */
  scopeCommit(commit: CommitInfo, diffStats: DiffStats): string[];

  /** Get all commits affecting a specific package */
  filterForPackage(commits: CommitInfo[], packagePath: string): CommitInfo[];
}

interface PackageConfig {
  name: string;           // e.g. "@my-org/core"
  path: string;           // e.g. "packages/core"
  changelogPath: string;  // e.g. "packages/core/CHANGELOG.md"
}
```

**Testing**:
- `test-detect-npm-workspaces`: Packages detected from `package.json` workspaces field
- `test-detect-pnpm-workspace`: Packages detected from `pnpm-workspace.yaml`
- `test-scope-commit-to-package`: Commit touching `packages/core/src/index.ts` scoped to `@my-org/core`
- `test-scope-commit-multiple-packages`: Commit touching files in two packages scoped to both
- `test-root-commit-scoping`: Changes to root-level files (`.github/`, `README.md`) handled correctly

#### 10.2 — Per-Package Version & Changelog
**What**: Generate independent versions and changelogs for each package in a monorepo.

**Design**:
```typescript
// Updated generate pipeline for monorepo:
// For each package:
//   1. Filter commits to those affecting this package
//   2. Classify commits
//   3. Calculate per-package version bump
//   4. Generate per-package changelog entries
//   5. Render per-package CHANGELOG.md
//   6. Optionally render a root-level combined changelog

// CLI: changelog-gen generate --monorepo --package @my-org/core
// Or:  changelog-gen generate --monorepo --all-packages
```

**Testing**:
- `test-per-package-changelog`: Each package gets its own CHANGELOG.md
- `test-per-package-versioning`: Package A bumps minor, Package B bumps patch independently
- `test-combined-changelog`: Root changelog aggregates all package changes
- `test-cross-package-breaking`: Breaking change in shared package flagged in dependent packages

---

## Phase 11: Advanced Features

### Purpose
Implement the remaining differentiating features: role-aware variants, cross-release summaries, compliance audit trail, and GDPR support.

### Tasks

#### 11.1 — Role-Aware Output Variants
**What**: Support configurable role definitions beyond the built-in developer/user/admin audiences.

**Design**:
```typescript
// Extend config to allow custom audience definitions:
{
  "audiences": [
    {
      "name": "security_team",
      "description": "Focus on CVEs, dependency vulnerabilities, auth changes",
      "includeCategories": ["Security", "Fixed"],
      "excludeScopes": [],
      "promptInstructions": "Emphasize security impact, CVE numbers, and remediation steps"
    }
  ]
}
```

**Testing**:
- `test-custom-audience-definition`: Custom "security_team" audience renders correctly
- `test-audience-category-filter`: Security audience only sees Security and Fixed categories
- `test-audience-prompt-customization`: Custom prompt instructions affect LLM output

#### 11.2 — Cross-Release Summary
**What**: Generate a narrative summary across multiple releases for stakeholder communication.

**Design**:
```typescript
// src/generator/cross-release-summary.ts

export class CrossReleaseSummarizer {
  constructor(private llmProvider: LLMProvider);

  /**
   * Generate a narrative summary of what changed between two versions.
   * Example: "Between v1.0.0 and v2.0.0, the platform gained SSO authentication,
   *           improved search performance by 40%, and fixed 23 bugs including 2 security issues."
   */
  async summarize(
    fromVersion: string,
    toVersion: string,
    releases: ReleaseInfo[]
  ): Promise<string>;
}

// CLI: changelog-gen summary --from v1.0.0 --to v2.0.0
```

**Testing**:
- `test-summary-across-3-releases`: Narrative covers all changes in version range
- `test-summary-highlights-breaking`: Breaking changes prominently mentioned
- `test-summary-counts-accurate`: "Fixed 23 bugs" reflects actual count
- `test-summary-audience-aware`: Summary tailored to specified audience

#### 11.3 — Compliance Audit Trail
**What**: Provide bidirectional traceability from release note entries to commits, PRs, and issues.

**Design**:
```typescript
// src/cli/commands/audit.ts

export async function auditCommand(options: { release: string }): Promise<void> {
  // Render an audit report for a specific release:
  // - Each entry with its source commits (SHA, author, date)
  // - Linked PRs (number, title, reviewer)
  // - Linked issues (key, title, status)
  // - Classification method and confidence
  // - AI model used and prompt hash
  // - Timestamp of each action in the pipeline
}

// CLI: changelog-gen audit --release v1.3.0 --format json
// Output: JSON document with full traceability chain
```

**Testing**:
- `test-audit-traces-to-commits`: Each entry links back to source commit SHAs
- `test-audit-traces-to-issues`: Each entry links to Jira/Linear issue keys
- `test-audit-shows-ai-provenance`: AI model, confidence, and prompt hash recorded
- `test-audit-json-export`: Audit report exported as structured JSON

#### 11.4 — GDPR Data Handling
**What**: Implement GDPR-compliant handling of author personal data (names, emails) in stored changelogs and audit trails.

**Design**:
```typescript
// src/core/gdpr.ts

export class GDPRHandler {
  constructor(private db: ChangelogDB);

  /**
   * Erase personal data for a specific email address.
   * Updates all JSONB author_info fields to {gdpr_erased: true, erased_at: ...}.
   * Preserves commit and entry data for referential integrity.
   */
  async eraseAuthorData(email: string): Promise<{ recordsUpdated: number }>;

  /**
   * List all stored personal data for an email address (DSAR).
   */
  async exportAuthorData(email: string): Promise<AuthorDataExport>;
}
```

**Testing**:
- `test-erasure-removes-pii`: After erasure, name and email are null/redacted
- `test-erasure-preserves-commits`: Commit data remains intact (SHA, message, date)
- `test-data-export-complete`: All stored data for an email exported in JSON format
- `test-erasure-audit-logged`: Erasure action recorded in audit log

---

## Phase 12: Documentation, Testing & Release

### Purpose
Comprehensive documentation, end-to-end test suite, performance benchmarking, and initial public release.

### Tasks

#### 12.1 — Documentation
**What**: Write complete documentation: README, configuration reference, API reference, template authoring guide.

**Design**:
- `README.md`: Quick start, installation, basic usage, feature overview
- `docs/configuration.md`: Full configuration reference with examples
- `docs/templates.md`: Template authoring guide with Handlebars helper reference
- `docs/ci-cd.md`: GitHub Actions and GitLab CI integration guide
- `docs/providers.md`: Setup guides for GitHub, GitLab, Jira, Linear
- `docs/monorepo.md`: Monorepo configuration and workflow
- `docs/api.md`: Programmatic API reference (for use as a library)

**Testing**:
- `test-docs-links-valid`: All internal links resolve correctly
- `test-docs-code-examples-run`: Code examples in docs are tested and functional
- `test-readme-quick-start`: Quick start instructions produce a working changelog

#### 12.2 — End-to-End Test Suite
**What**: Build a comprehensive E2E test suite using real git repositories with known commit histories.

**Design**:
```typescript
// test/e2e/
// - fixtures/: pre-built git repos with known commit histories
//   - conventional-repo/: 100% Conventional Commits
//   - freetext-repo/: 0% Conventional Commits (free-text only)
//   - mixed-repo/: 50/50 mix
//   - monorepo/: multi-package workspace
//   - large-repo/: 1000+ commits for performance testing
```

**Testing**:
- `test-e2e-conventional-repo`: Full pipeline produces correct KaC changelog
- `test-e2e-freetext-repo`: AI classification produces meaningful entries from free-text
- `test-e2e-mixed-repo`: Hybrid pipeline handles mixed commit styles
- `test-e2e-monorepo`: Per-package changelogs generated correctly
- `test-e2e-dual-audience`: Developer and user-facing outputs differ appropriately
- `test-e2e-github-action`: Action workflow runs end-to-end in test environment
- `test-e2e-incremental`: Second run on same repo only processes new commits

#### 12.3 — Performance Benchmarking
**What**: Benchmark the pipeline on large repositories and optimize bottlenecks.

**Design**:
- Target: 1000 commits classified and rendered in under 60 seconds
- LLM API calls are the bottleneck: batch processing, parallel requests, prompt caching
- Git operations: use `simple-git` stream mode for large repos
- Database: batch inserts for commits; connection pooling

**Testing**:
- `test-perf-1000-commits`: Full pipeline completes in <60s for 1000 commits
- `test-perf-ai-batch-size`: Optimal batch size (10 commits/request) validated
- `test-perf-prompt-cache-hit`: Second run shows prompt cache hits (reduced token usage)

#### 12.4 — NPM Package & GitHub Action Publication
**What**: Publish the npm package and GitHub Action to their respective registries.

**Design**:
- npm: `changelog-gen` package published to npm registry
- GitHub Marketplace: Action published as `changelog-gen/changelog-gen-action`
- Release automation: use the tool itself to generate its own release notes (dogfooding)

**Testing**:
- `test-npm-install-global`: `npm install -g changelog-gen` works on clean Node.js 20
- `test-npx-execution`: `npx changelog-gen --help` works without global install
- `test-action-marketplace`: Action usable via `uses: changelog-gen/changelog-gen-action@v1`
- `test-dogfood`: The tool generates its own CHANGELOG.md successfully

---

## Phase Summary & Dependencies

```
Phase 1: Scaffolding & Types           (no dependencies)
Phase 2: Git & Conventional Commits    (depends on Phase 1)
Phase 3: AI Classification             (depends on Phase 2)
Phase 4: Entry Generation & Audiences  (depends on Phase 3)
Phase 5: GitHub & GitLab Integration   (depends on Phase 4)
Phase 6: Jira & Linear Integration     (depends on Phase 5)
Phase 7: Database & Persistence        (depends on Phase 4; parallel with 5-6)
Phase 8: Output Renderers & Templates  (depends on Phase 4; parallel with 5-7)
Phase 9: Publishing & Distribution     (depends on Phases 5, 7, 8)
Phase 10: Monorepo Support             (depends on Phase 7)
Phase 11: Advanced Features            (depends on Phases 7, 8, 9)
Phase 12: Documentation & Release      (depends on all prior phases)
```

Phases 5-6, 7, and 8 can be developed in parallel after Phase 4 is complete. The critical path is: 1 -> 2 -> 3 -> 4 -> 9 -> 12.

---

## Definition of Done (per phase)

Each phase is complete when:

1. **All tasks implemented**: Every task in the phase has working code merged to the main branch.
2. **All tests pass**: Every named test scenario passes in CI. Coverage for new code exceeds 85%.
3. **No regressions**: All tests from prior phases continue to pass.
4. **Type safety**: Zero TypeScript `any` escapes; strict mode enabled throughout.
5. **Error handling**: All error paths produce actionable messages with context (file path, commit SHA, API endpoint).
6. **Logging**: Structured logging at appropriate levels (debug for API calls, info for pipeline steps, warn for degraded operation, error for failures).
7. **Documentation**: New CLI flags, configuration options, and API methods have inline JSDoc documentation.
8. **Linting**: Code passes ESLint with no warnings; consistent formatting via Prettier.
9. **Working increment**: The CLI produces useful output at the end of every phase (Phase 2+). Each phase extends the capability without breaking the previous phases' functionality.
10. **Dogfooding**: From Phase 4 onward, the tool is used to generate its own changelog for each phase's release.
