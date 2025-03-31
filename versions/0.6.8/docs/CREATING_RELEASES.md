# Creating Releases for Punch Card Project

This document describes how to create and publish a new release of the Punch Card Project.

## Prerequisites

- Git command line tools
- (Optional) GitHub CLI for easier release creation
- Access to the GitHub repository with write permissions

## Release Process

### 1. Update Version Information

Before creating a release, ensure the version numbers are updated in the following files:

- `src/utils/version_info.py` - Update the `VERSION` variable
- `src/main.py` - Update the version displayed when running with `--version` flag
- `punch_card_settings.json` - Add or update the `"version"` field

### 2. Create Release Notes

Create detailed release notes in Markdown format:

```bash
# Create a file in the release_notes directory
touch release_notes/vX.Y.Z.md
```

Follow the template from previous release notes. Make sure to cover:
- Overview of the release
- Key features and changes
- Bug fixes
- Compatibility notes

### 3. Using the Release Script

We provide a helper script for creating releases:

```bash
# Run the release script
./create_release.sh

# Alternatively, specify a version
./create_release.sh 0.6.6
```

The script will:
- Verify version information consistency
- Create a Git tag
- Push the tag to GitHub

### 4. GitHub Actions Automated Build

Once the tag is pushed, our GitHub Actions workflow will automatically:
- Create a GitHub release
- Build executables for Linux, macOS, and Windows
- Attach release notes and executables to the release

### 5. Manual Release Creation (if needed)

If automated builds fail or you prefer a manual release:

1. Go to the [Releases page](https://github.com/yourusername/punch-card-project/releases)
2. Click "Draft a new release"
3. Enter the tag version (e.g., `v0.6.6`)
4. Set the release title (e.g., "Punch Card Project v0.6.6")
5. Copy and paste the release notes 
6. Upload any additional assets
7. Click "Publish release"

Alternatively, use the GitHub CLI:

```bash
gh release create v0.6.6 \
  --title "Punch Card Project v0.6.6" \
  --notes-file release_notes/v0.6.6.md
```

## Creating Pre-releases

For pre-release versions, follow the same steps but:
- Use a suffix like `-beta.1` in the version (e.g., `0.6.6-beta.1`)
- When publishing on GitHub, check the "This is a pre-release" option

## After Release

After publishing a release:
1. Update the main README.md with the latest version
2. Increment version in development branch to next planned version + `-dev`
3. Notify users via appropriate channels 