# Branching and Release Strategy

This document outlines the branching strategy and release workflow for the Punch Card Project.

## Branch Structure

We follow a modified Git Flow branching model:

### Main Branches

- **main**: The primary branch containing production-ready code
- **develop**: The development branch where features are integrated

### Supporting Branches

- **feature/xxx**: For developing new features (branched from `develop`)
- **release/x.y.z**: For preparing releases (branched from `develop`)
- **hotfix/x.y.z**: For critical bug fixes to production (branched from `main`)

## Workflow

### Feature Development

1. Create a feature branch from `develop`:
   ```bash
   git checkout develop
   git checkout -b feature/my-feature
   ```

2. Develop the feature with regular commits

3. When complete, merge back to `develop`:
   ```bash
   git checkout develop
   git merge --no-ff feature/my-feature
   git push origin develop
   ```

### Release Process

1. Create a release branch from `develop`:
   ```bash
   git checkout develop
   git checkout -b release/x.y.z
   ```

2. Update version numbers in:
   - `src/utils/version_info.py`
   - `src/main.py`
   - `punch_card_settings.json`

3. Create release notes in `release_notes/vx.y.z.md`

4. Test, fix bugs, and commit changes directly to the release branch

5. When ready to release, merge to both `main` and `develop`:
   ```bash
   # Merge to main
   git checkout main
   git merge --no-ff release/x.y.z
   git tag -a vx.y.z -m "Version x.y.z release"
   
   # Merge back to develop
   git checkout develop
   git merge --no-ff release/x.y.z
   
   # Push changes
   git push origin main develop --tags
   ```

6. Create a GitHub release using:
   ```bash
   gh release create vx.y.z --title "Punch Card Project vx.y.z" --notes-file release_notes/vx.y.z.md
   ```

### Hotfix Process

1. Create a hotfix branch from `main`:
   ```bash
   git checkout main
   git checkout -b hotfix/x.y.z
   ```

2. Fix the critical bug and update version numbers

3. When complete, merge to both `main` and `develop`:
   ```bash
   # Merge to main
   git checkout main
   git merge --no-ff hotfix/x.y.z
   git tag -a vx.y.z -m "Version x.y.z hotfix"
   
   # Merge to develop
   git checkout develop
   git merge --no-ff hotfix/x.y.z
   
   # Push changes
   git push origin main develop --tags
   ```

## Version Numbering

We follow semantic versioning (SemVer):

- **Major version (x)**: Incremented for incompatible API changes
- **Minor version (y)**: Incremented for backward-compatible new features
- **Patch version (z)**: Incremented for backward-compatible bug fixes

## Tag Management

All releases should be tagged with a version number prefixed with 'v':
```bash
git tag -a vx.y.z -m "Version x.y.z release"
```

## Branch Cleanup

After merging feature, release, or hotfix branches, they should be deleted:
```bash
git branch -d feature/my-feature
```

For remote branches:
```bash
git push origin --delete feature/my-feature
``` 