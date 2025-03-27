#!/bin/bash
# create_release.sh - Create and push a new release tag to GitHub
#
# This script creates a git tag for the specified version and pushes it to GitHub.
# It also creates a GitHub release using the release notes.

# Set the version (default to the one in version_info.py if not provided)
VERSION=${1:-$(python -c "from src.utils.version_info import VERSION; print(VERSION)")}

echo "====================================================="
echo "Creating release v$VERSION for Punch Card Project"
echo "====================================================="

# Check if the version string is valid
if [[ ! $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: Version should be in format X.Y.Z"
    exit 1
fi

# Check if tag already exists
if git rev-parse "v$VERSION" >/dev/null 2>&1; then
    echo "Error: Tag v$VERSION already exists!"
    exit 1
fi

# Check if we have uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "Warning: You have uncommitted changes."
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborting release creation."
        exit 1
    fi
fi

# Check if release notes exist
RELEASE_NOTES="release_notes/v$VERSION.md"
if [ ! -f "$RELEASE_NOTES" ]; then
    echo "Error: Release notes file $RELEASE_NOTES not found!"
    exit 1
fi

# Make sure settings version is updated
SETTINGS_FILE="punch_card_settings.json"
if ! grep -q "\"version\": \"$VERSION\"" "$SETTINGS_FILE"; then
    echo "Error: Version in settings file doesn't match!"
    echo "Please update $SETTINGS_FILE with version: $VERSION"
    exit 1
fi

# Make sure version_info.py is updated
if ! grep -q "VERSION = \"$VERSION\"" "src/utils/version_info.py"; then
    echo "Error: VERSION in src/utils/version_info.py doesn't match!"
    echo "Please update src/utils/version_info.py with VERSION = \"$VERSION\""
    exit 1
fi

# Create tag with release message
echo "Creating tag v$VERSION..."
git tag -a "v$VERSION" -m "Version $VERSION release"

# Push the tag to remote
echo "Pushing tag to remote repository..."
git push origin "v$VERSION"

echo
echo "====================================================="
echo "Tag v$VERSION created and pushed to GitHub"
echo "====================================================="
echo
echo "Now create a release on GitHub:"
echo "1. Go to https://github.com/your-username/punch-card-project/releases"
echo "2. Click 'Draft a new release'"
echo "3. Select the tag v$VERSION"
echo "4. Set the title to 'Punch Card Project v$VERSION'"
echo "5. Copy and paste the release notes from $RELEASE_NOTES"
echo "6. Upload relevant assets if needed"
echo "7. Click 'Publish release'"
echo
echo "Alternatively, use the GitHub CLI to create a release:"
echo "gh release create v$VERSION --title \"Punch Card Project v$VERSION\" --notes-file $RELEASE_NOTES"
echo 