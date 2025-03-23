# Git Versioning Strategy for the Punch Card Project

This document outlines the Git branching strategy and versioning approach for the Punch Card Project.

## Overview

The Punch Card Project uses a modified [GitFlow](https://nvie.com/posts/a-successful-git-branching-model/) workflow for version control. This approach provides a structured way to manage releases, features, and hotfixes while maintaining clear versioning and historical reference points.

## Branch Structure

The repository maintains several types of branches, each with a specific purpose:

| Branch Type | Naming Convention | Purpose |
|-------------|-------------------|---------|
| `master` | N/A | Main production branch containing stable code |
| `develop` | N/A | Integration branch for new features |
| `feature/*` | `feature/<feature-name>` | Branches for developing new features |
| `release/*` | `release/v<version>` | Preparation branches for upcoming releases |
| `hotfix/*` | `hotfix/v<version>` | Emergency fixes for production code |
| `v*.*.*` | `v<version>` | Version branches that reflect release points (e.g., v0.5.0) |

## Versioning Approach

The project follows a semantic versioning approach (major.minor.patch):

- **Major versions (X.0.0)**: Significant changes, major rewrites, or incompatible API changes
- **Minor versions (0.X.0)**: New features and functionality in a backward-compatible manner
- **Patch versions (0.0.X)**: Bug fixes and small improvements that don't change functionality

## Tools

The project provides tools to manage the Git workflow:

- **version_manager.py**: Handles version snapshots and file archiving
- **git_version_manager.py**: Manages Git branches and integrates with version_manager.py

## Standard Workflows

### Feature Development

1. **Create a feature branch**:
   ```bash
   ./scripts/git_version_manager.py feature new-display-component
   ```

2. **Work on the feature**:
   Make changes, commit frequently with descriptive messages.

3. **Complete the feature**:
   ```bash
   ./scripts/git_version_manager.py finish-feature new-display-component
   ```
   This merges the feature into `develop` and deletes the feature branch.

### Release Process

1. **Create a release branch**:
   ```bash
   ./scripts/git_version_manager.py release 0.6.0
   ```
   This will:
   - Create a `release/v0.6.0` branch from `develop`
   - Update version numbers in README.md
   - Allow for final testing and adjustments

2. **Complete the release**:
   ```bash
   ./scripts/git_version_manager.py finish-release 0.6.0
   ```
   This will:
   - Merge the release branch into `master`
   - Create a `v0.6.0` tag and version branch
   - Generate a version snapshot in the `versions/` directory
   - Merge changes back into `develop`
   - Delete the release branch

### Hotfix Process

1. **Create a hotfix branch**:
   ```bash
   ./scripts/git_version_manager.py hotfix 0.5.3
   ```
   This creates a branch from `master` to fix an urgent issue.

2. **Complete the hotfix**:
   ```bash
   ./scripts/git_version_manager.py finish-hotfix 0.5.3
   ```
   This will:
   - Merge the hotfix into `master` and `develop`
   - Create a version tag and branch
   - Generate a version snapshot
   - Delete the hotfix branch

## Branch Lifecycle Visualization

```
                      ┌───────────┐
                      │  master   │
                      └─────┬─────┘
                            │
               ┌────────────┴────────────┐
               │                         │
     ┌─────────▼──────────┐     ┌────────▼───────┐
     │ hotfix/v0.5.3      │     │ release/v0.6.0 │
     └─────────┬──────────┘     └────────┬───────┘
               │                         │
               │                         │
      ┌────────▼────────┐      ┌─────────▼────────┐
      │    v0.5.3       │      │     v0.6.0       │
      └────────┬────────┘      └─────────┬────────┘
               │                         │
               │                         │
               └──────────┐    ┌─────────┘
                          │    │
                     ┌────▼────▼───┐
                     │   develop   │
                     └──────┬──────┘
                            │
                ┌───────────┴──────────┐
                │                      │
      ┌─────────▼──────────┐  ┌────────▼────────┐
      │ feature/display    │  │ feature/api     │
      └─────────┬──────────┘  └────────┬────────┘
                │                      │
                └──────────┬───────────┘
                           │
                   ┌───────▼───────┐
                   │    develop    │
                   └───────────────┘
```

## Version Snapshots

In addition to Git versioning, the project maintains complete snapshots of each release in the `versions/` directory. These snapshots contain:

1. All source code at the time of release
2. Configuration files
3. README.md as it existed
4. Test files
5. A version_info.txt file with metadata

This provides both Git-based version control and physical version archives for complete reference.

## Checking Status

To check the current versioning status:

```bash
./scripts/git_version_manager.py status
```

This will show:
- Current branch and version
- All version branches
- Feature, release, and hotfix branches
- Available tags
- Next steps

## Initial Setup

If you're starting with a fresh repository or need to set up the workflow:

```bash
./scripts/git_version_manager.py setup
```

This will:
- Create a `develop` branch if it doesn't exist
- Create version branches for any existing tags
- Set up the initial branch structure

## Best Practices

1. **Never commit directly to `master` or `develop`**
   - Always use feature, release, or hotfix branches

2. **Descriptive commit messages**
   - Start with a verb (Add, Fix, Update, etc.)
   - Explain what changed and why

3. **Regular integration**
   - Merge `develop` into feature branches regularly to reduce conflicts

4. **Clean feature branches**
   - Each feature branch should focus on a single feature or component

5. **Thorough testing before releases**
   - Test thoroughly in the release branch before finalizing

6. **Documentation updates**
   - Update documentation, especially for new features or API changes

## Conclusion

This versioning strategy provides a structured approach to managing the Punch Card Project's development. It ensures clear version history, makes it easy to track changes, and provides both Git-based versioning and physical version archives.

For questions or issues with this workflow, contact the project maintainers or open an issue in the repository. 