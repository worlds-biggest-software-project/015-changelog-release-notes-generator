# Changelog & Release Notes Generator

AI-powered changelog and release notes automation that generates human-quality summaries from unstructured commit messages, PR descriptions, and issue tickets — eliminating the "what changed" documentation burden.

## The Problem

Release note generation is trapped in a specification straitjacket:

- **Rule-based tools require Conventional Commits** — ~90% of projects don't use them
- **Detection-only tools stop at diagnosis** — semantic-release and git-cliff surface what changed; none generate what it *means* to users
- **The developer-to-user gap is unsolved** — every tool produces internal `CHANGELOG.md` but no tool generates user-facing "What's New" announcements from the same source
- **Issue tracker context is ignored** — Jira/Linear tickets have business context that git commits lack; no tool synthesizes this

Current state: developers write changelogs manually (tedious, error-prone) or rely on auto-generated lists of commit subjects (low quality, developer-facing only).

## What This Does

### Free-Text Commit Classification (AI-Native)
- **Reads unstructured commit messages** — no Conventional Commits required
- **LLM infers type (feature/fix/breaking/internal) and scope** from commit message, diff summary, and PR description
- **Works out-of-the-box for 90% of projects** — the gap that rule-based tools fail on
- **Handles inconsistent conventions** — mixed Conventional Commits + free-text in the same repo

### Dual-Audience Output
- **Generates both developer CHANGELOG and user-facing "What's New"** from the same source
- **Developer output**: technical details (API changes, deprecated methods, internal refactors)
- **User output**: benefit statements (features added, problems fixed, performance improved)
- **Internal refactors filtered out** of user-facing notes automatically
- **No open-source tool does this** — gap between Beamer/Headway (SaaS, user-facing only) and semantic-release/git-cliff (OSS, internal only)

### Issue Tracker Integration
- **Fetches linked Jira/Linear/GitHub Issues** for context
- **Incorporates business-level descriptions** — not just code-level reasoning
- **Produces better release notes** by understanding *why* the change matters, not just *what* changed
- **Attribute changes to business priorities** — which features delivered for which customer requests

### Role-Aware Personalization
- **Different release notes for different roles** — inspired by SmartNote research (2025)
- **Admin variant**: security fixes, performance improvements, operational notes
- **User variant**: new features, problem solutions, benefit statements
- **Developer variant**: API changes, deprecations, internal refactors

## Key Differentiators

| Feature | This Platform | semantic-release | git-cliff | release-please | WhatShipped | Beamer |
|---------|---|---|---|---|---|---|
| **Free-text commits** | ✓ (LLM-based) | Requires Conventional | Requires structure | Requires Conventional | ✓ (Cloud) | — |
| **Dual-audience output** | ✓ | — | — | — | — | ✓ SaaS only |
| **Issue tracker integration** | ✓ (Jira/Linear) | — | — | — | — | — |
| **Role-aware variants** | ✓ | — | — | — | — | — |
| **Open source** | ✓ | ✓ (MIT) | ✓ (MIT) | ✓ (Apache) | — (SaaS) | — (SaaS) |
| **CI/CD integration** | ✓ | ✓ | ✓ | ✓ | — | — |

## Market & Opportunity

- **Market size**: $2.11B (2024) → $4.5B (2035) at 7.1% CAGR (release management subset)
- **Adoption barrier**: ~90% of projects don't use Conventional Commits — rule-based tools are useless for them
- **Buyers**: Development teams (all sizes), DevOps engineers, product managers, technical writers
- **Open-source gap**: No OSS tool generates both developer and user-facing notes from the same source

## Research Foundation

- **~90% of projects don't enforce Conventional Commits** — research finding from ICSE 2025 study
- **52 documented classification challenges** in Conventional Commits (ICSE 2025)
- **14% of commits are empty; 66% have minimal descriptions** (arXiv:2202.02974, 2022)
- **Commit message quality correlates with software defect proneness** (ICSE 2023)
- **LLM-based commit classification outperforms rule-based approaches by 12 F1 points** (Fäerber et al., COMPSAC 2023)

## Quick Start

```bash
# Generate changelog from git history
changelog-gen --since=v1.0.0 --until=HEAD --output=CHANGELOG.md

# Generate dual-audience output
changelog-gen --since=v1.0.0 \
  --developer-output=CHANGELOG-DEV.md \
  --user-output=WHATSNEW.md

# Integrate with issue tracker
changelog-gen --jira-url=https://jira.company.com \
  --jira-project=MYAPP \
  --include-context

# In CI/CD pipeline
changelog-gen --auto --commit-to=main --create-release
```

## Target Users

1. **Development Teams (all sizes)** — eliminate manual changelog writing
2. **DevOps/Release Engineers** — automate release note generation in CI/CD
3. **Product Managers** — generate user-facing "What's New" announcements
4. **Technical Writers** — auto-generate draft release notes for refinement
5. **Open-source Projects** — good community communication with minimal effort

## Related Standards

- Conventional Commits Specification (v1.0.0) — machine-parseable commit format
- Semantic Versioning (SemVer v2.0.0) — version signaling aligned with changes
- Keep a Changelog (v1.1.0) — human-facing changelog format standard
- Git Tagging Conventions — release tag naming and management

---

Built on research from SmartNote (arXiv:2505.17977, 2025), ICSE 2025 Conventional Commits classification study, and production learnings from semantic-release, release-please, and WhatShipped. [Read the full research](./research.md) | [Feature roadmap](./features.md)
