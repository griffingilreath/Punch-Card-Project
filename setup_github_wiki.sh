#!/bin/bash

# Setup GitHub Wiki for Punch Card Project
# This script will:
# 1. Clone the wiki repository (after it's been enabled on GitHub)
# 2. Copy prepared wiki content to the wiki repository
# 3. Commit and push changes

# Variables
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
WIKI_REPO_URL="git@github.com:griffingilreath/Punch-Card-Project.wiki.git"
TEMP_WIKI_DIR="$HOME/punch_card_wiki"
WIKI_DIR="$PROJECT_DIR/../Punch-Card-Project.wiki"

echo "===== Punch Card Project Wiki Setup ====="
echo "This script will set up and populate your GitHub Wiki."
echo "Make sure you've enabled the Wiki feature in your GitHub repository settings first!"
echo "--------------------------------------------"

# Check if the wiki content exists in the temporary directory
if [ ! -d "$TEMP_WIKI_DIR" ]; then
    echo "Error: The temporary wiki content directory ($TEMP_WIKI_DIR) doesn't exist."
    echo "Please run the wiki content preparation script first."
    exit 1
fi

# Clone the wiki repository if it doesn't exist
if [ ! -d "$WIKI_DIR" ]; then
    echo "Cloning the wiki repository..."
    cd "$(dirname "$PROJECT_DIR")"
    git clone "$WIKI_REPO_URL" || {
        echo "Error: Failed to clone the wiki repository."
        echo "Make sure you've enabled the Wiki feature in your GitHub repository settings."
        echo "The wiki URL should be: $WIKI_REPO_URL"
        exit 1
    }
fi

# Copy the prepared wiki content to the wiki repository
echo "Copying wiki content..."
cp -r "$TEMP_WIKI_DIR"/* "$WIKI_DIR"/ || {
    echo "Error: Failed to copy wiki content."
    exit 1
}

# Commit and push changes
echo "Committing and pushing changes..."
cd "$WIKI_DIR"
git add .
git commit -m "Initial wiki content setup" || {
    echo "Warning: No changes to commit or commit failed."
}
git push || {
    echo "Error: Failed to push changes to the wiki repository."
    echo "Check your SSH keys and repository permissions."
    exit 1
}

echo "--------------------------------------------"
echo "✅ GitHub Wiki setup complete!"
echo "Your wiki has been populated with the initial content."
echo "You can now visit your wiki at: https://github.com/griffingilreath/Punch-Card-Project/wiki"
echo "--------------------------------------------" 