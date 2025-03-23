# GitHub Wiki Setup Instructions

This document explains how to set up and publish the GitHub wiki for the Punch Card Project.

## Prerequisites

1. GitHub repository with wiki feature enabled
2. SSH key configured for GitHub access
3. Git installed on your local machine

## Step 1: Prepare Wiki Content

We've already prepared the wiki content in `~/punch_card_wiki/`. This content includes:

- Home page with project overview
- Sidebar navigation
- Research documentation pages (Design Language, Interface Design History, etc.)
- Technical documentation pages
- API documentation
- Installation and usage guides
- Contributing guidelines
- Version information pages

If you want to update or regenerate this content, you can use the script:

```bash
./scripts/prepare_wiki_content.sh
```

This script will:
1. Create the `~/punch_card_wiki/` directory if it doesn't exist
2. Copy documentation from the `docs/` directory
3. Create necessary wiki pages (Home, Sidebar, Footer)
4. Convert filenames to the GitHub wiki naming convention

## Step 2: Publish Wiki Content

To publish the content to your GitHub wiki, run:

```bash
./setup_github_wiki.sh
```

This script will:
1. Clone the wiki repository (you need to have enabled the wiki feature in your GitHub repository settings)
2. Copy the prepared content to the wiki repository
3. Commit and push the changes

## Step 3: Verify Wiki

After running the setup script, you can verify your wiki at:
https://github.com/griffingilreath/Punch-Card-Project/wiki

## Updating the Wiki

To update the wiki in the future:

1. Make changes to the documentation in the `docs/` directory
2. Run `./scripts/prepare_wiki_content.sh` to update the wiki content
3. Run `./setup_github_wiki.sh` to publish the changes

## Troubleshooting

- **Error cloning wiki repository**: Make sure you've enabled the wiki feature in your GitHub repository settings
- **Error pushing changes**: Check your SSH key configuration and GitHub permissions
- **Missing content**: Verify that your documentation files are in the correct format and location

## For Future Enhancements

- Consider adding a script to check for broken wiki links
- Add a script to automatically update version history pages
- Implement a continuous integration workflow to automatically update the wiki on commits to main/master 