#!/bin/bash

# Update version in README
python3 update_version.py

# Add and commit changes
git add README.md
git commit -m "docs: update README version to match settings"

# Push to all branches
git push origin testing
git checkout stable
git cherry-pick HEAD~0
git push origin stable
git checkout main
git cherry-pick HEAD~0
git push origin main
git checkout testing 