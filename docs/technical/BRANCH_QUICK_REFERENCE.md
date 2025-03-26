# Branch Management Quick Reference

## Common Commands

### Checking Branches
```bash
# List all local branches
git branch

# List all branches (local and remote)
git branch -a

# See current branch
git status
```

### Working with Branches
```bash
# Switch to a branch
git checkout <branch-name>

# Create and switch to a new branch
git checkout -b <new-branch-name>

# Pull latest changes from current branch
git pull

# Push changes to remote
git push
```

### Our Branch Workflow

#### Starting New Work
```bash
# Ensure you're on testing branch
git checkout testing

# Pull latest changes
git pull

# Create feature branch (optional for complex features)
git checkout -b feature/my-feature
```

#### Merging Changes
```bash
# Merge testing into stable
git checkout stable
git pull
git merge testing
git push

# Merge stable into main
git checkout main
git pull
git merge stable
git push
```

#### Creating Releases
```bash
# Tag a release on main
git checkout main
git pull
git tag -a v1.0.0 -m "Version 1.0.0 release"
git push --tags
```

## Quick Branch Descriptions

- **main**: Production-ready code
- **stable**: Pre-release staging
- **testing**: Active development 