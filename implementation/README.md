# Changelog & Release Notes Generator

An AI-native tool for automatically generating changelogs and release notes from git commits.

## Features

- Parses conventional commit messages
- Categorizes changes (features, fixes, docs, etc.)
- Generates markdown-formatted changelogs
- Supports generating since specific tags or commits

## Installation

1. Clone or download the repository
2. Ensure Python 3.6+ is installed
3. Make the script executable: `chmod +x changelog_generator.py`

## Usage

```bash
# Generate changelog for all commits
python3 changelog_generator.py

# Generate changelog since a specific tag
python3 changelog_generator.py --since v1.0.0

# Specify version and output file
python3 changelog_generator.py --version 1.1.0 --output CHANGELOG.md
```

## Conventional Commits

This tool works best with conventional commit format:

```
type(scope): description

[optional body]
```

Types: feat, fix, docs, style, refactor, test, chore, perf, ci, build

## Example Output

```markdown
# Changelog

## [1.1.0]

### Features
- Add user authentication
- Implement dark mode

### Bug Fixes
- Fix login validation
- Resolve memory leak

### Documentation
- Update API docs
```

## Future Enhancements

- AI-powered commit message improvement
- Automatic release note summarization
- Integration with GitHub/GitLab releases
- Multi-language support