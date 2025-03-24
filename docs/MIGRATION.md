# Migrating to a new repository

If you need to migrate to a new repository to avoid API key history issues:

1. Create a new empty repository on GitHub
2. Run these commands in your local repository:

```bash
# Set your new repository URL
NEW_REPO_URL=https://github.com/username/new-repo-name.git

# Add the new remote
git remote add new-origin $NEW_REPO_URL

# Push your current branch and all tags to the new repository
git push new-origin temp_clean_branch:main
git push new-origin v0.5.9-security
```

3. Then switch to using the new repository going forward.
