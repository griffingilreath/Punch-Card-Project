# GitHub Wiki Update Guide

This guide provides instructions for updating the Punch Card Project's GitHub wiki with version history and other documentation.

## Updating the Wiki with Version History

We've created a script (`scripts/update_wiki.sh`) that generates wiki content in the `~/punch_card_wiki` directory. This content needs to be manually copied to your GitHub wiki repository.

### Step 1: Run the wiki update script

```bash
./scripts/update_wiki.sh
```

This will create or update content in the `~/punch_card_wiki` directory, including:
- Version-History.md
- _Sidebar.md

### Step 2: Clone the wiki repository (if not already done)

```bash
git clone https://github.com/griffingilreath/Punch-Card-Project.wiki.git
```

This will create a `Punch-Card-Project.wiki` directory in your current location.

### Step 3: Copy the content to the wiki repository

```bash
cp -r ~/punch_card_wiki/* /path/to/Punch-Card-Project.wiki/
```

Replace `/path/to/Punch-Card-Project.wiki/` with the actual path to your cloned wiki repository.

### Step 4: Commit and push the changes

```bash
cd /path/to/Punch-Card-Project.wiki/
git add .
git commit -m "Update wiki content with Version History"
git push origin master
```

## Wiki Structure

The wiki is structured with the following main sections:

1. **Getting Started**
   - Home
   - Installation
   - Quick Start Guide

2. **Documentation**
   - Version History
   - User Guide
   - API Reference
   - Configuration

3. **Development**
   - Contributing
   - Architecture
   - Testing

4. **Research**
   - Interface Design History
   - Punch Card Encoding
   - LED Implementation
   - Sociological Aspects

## Keeping Documentation In Sync

When making significant changes to the project, make sure to:

1. Update the Version History in both:
   - README.md
   - Version History Wiki page

2. Keep documentation links consistent between:
   - README.md
   - Wiki pages 
   - Documentation files

3. Update the version number in:
   - punch_card.py
   - README.md
   - Version History Wiki page

## Adding New Wiki Pages

To add a new wiki page:

1. Create the Markdown file in the `~/punch_card_wiki` directory
2. Update the _Sidebar.md file to include a link to your new page
3. Follow Steps 3-4 above to copy, commit, and push the changes

## Troubleshooting

If you encounter issues with wiki updates:

1. **Authentication problems**: Make sure you have the necessary permissions to push to the wiki
2. **Content not updating**: Check that you've copied the files to the correct location and pushed to the right branch
3. **Formatting issues**: Review the Markdown syntax in your files 