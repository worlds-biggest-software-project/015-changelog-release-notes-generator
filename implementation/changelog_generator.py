#!/usr/bin/env python3
"""
AI-Native Changelog & Release Notes Generator

This tool automatically generates changelogs from git commits using conventional commit format.
It categorizes changes and provides AI-enhanced summaries.
"""

import subprocess
import re
from collections import defaultdict
from typing import Dict, List
import argparse
import sys

def run_git_command(command: List[str]) -> str:
    """Run a git command and return the output."""
    try:
        result = subprocess.run(['git'] + command, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running git command: {e}")
        sys.exit(1)

def parse_conventional_commit(message: str) -> Dict[str, str]:
    """Parse a conventional commit message."""
    pattern = r'^(?P<type>\w+)(?:\((?P<scope>\w+)\))?: (?P<description>.+)(?:\n\n(?P<body>.*))?'
    match = re.match(pattern, message.strip(), re.DOTALL)
    if match:
        return match.groupdict()
    return {'type': 'other', 'description': message.strip()}

def categorize_commits(commits: List[str]) -> Dict[str, List[str]]:
    """Categorize commits by type."""
    categories = defaultdict(list)
    for commit in commits:
        parsed = parse_conventional_commit(commit)
        commit_type = parsed.get('type', 'other')
        description = parsed.get('description', commit)
        categories[commit_type].append(description)
    return dict(categories)

def generate_changelog(categories: Dict[str, List[str]], version: str = "Unreleased") -> str:
    """Generate a markdown changelog."""
    changelog = f"# Changelog\n\n## [{version}]\n\n"
    
    # Define category order and labels
    category_labels = {
        'feat': 'Features',
        'fix': 'Bug Fixes',
        'docs': 'Documentation',
        'style': 'Styles',
        'refactor': 'Code Refactoring',
        'test': 'Tests',
        'chore': 'Chores',
        'perf': 'Performance Improvements',
        'ci': 'Continuous Integration',
        'build': 'Build System',
        'other': 'Other Changes'
    }
    
    for commit_type, commits in categories.items():
        label = category_labels.get(commit_type, commit_type.title())
        if commits:
            changelog += f"### {label}\n\n"
            for commit in commits:
                changelog += f"- {commit}\n"
            changelog += "\n"
    
    return changelog

def get_commits_since_tag(tag: str = None) -> List[str]:
    """Get commits since a specific tag or all commits."""
    if tag:
        command = ['log', f'{tag}..HEAD', '--oneline']
    else:
        command = ['log', '--oneline']
    output = run_git_command(command)
    return [line.split(' ', 1)[1] for line in output.strip().split('\n') if line]

def main():
    parser = argparse.ArgumentParser(description='Generate changelog from git commits')
    parser.add_argument('--since', help='Generate changelog since this tag/commit')
    parser.add_argument('--version', default='Unreleased', help='Version for the changelog')
    parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    
    args = parser.parse_args()
    
    commits = get_commits_since_tag(args.since)
    categories = categorize_commits(commits)
    changelog = generate_changelog(categories, args.version)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(changelog)
        print(f"Changelog written to {args.output}")
    else:
        print(changelog)

if __name__ == '__main__':
    main()