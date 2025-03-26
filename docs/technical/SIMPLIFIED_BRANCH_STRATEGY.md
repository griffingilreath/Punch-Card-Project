# Simplified Branch Strategy for Punch Card Project

## Overview

This project uses a simplified three-branch strategy to manage development and releases:

1. **main** - The primary branch representing the latest stable release
2. **stable** - Contains thoroughly tested code ready for release
3. **testing** - Used for active development and integration testing

## Branch Purposes

### Main Branch
- Represents production code only
- All code must pass through stable before reaching main
- Tagged with version numbers for releases
- Protected from direct commits

### Stable Branch
- Contains code that has passed thorough testing
- Serves as a staging area before production
- Used for pre-release verification
- Should be stable enough for demo purposes

### Testing Branch
- Primary branch for active development
- All new features and bug fixes start here
- Undergoes continuous integration testing
- May contain experimental features

## Workflow

1. New development starts in the testing branch
2. When features are complete and tested, testing is merged into stable
3. After additional testing and verification, stable is merged into main
4. Releases are created by tagging the main branch

## Tagging Convention

- Release tags follow semantic versioning: v[MAJOR].[MINOR].[PATCH]
- Example: v0.6.1, v1.0.0, v1.2.3

## Best Practices

- Always pull before starting new work
- Create feature branches off testing for complex changes
- Use descriptive commit messages
- Tag all releases on the main branch
- Document significant changes in CHANGELOG.md 