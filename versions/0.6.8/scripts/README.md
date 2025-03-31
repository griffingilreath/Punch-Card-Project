# Scripts Directory

This directory contains utility scripts for maintaining the Punch Card Project.

## Available Scripts

### `update_wiki.sh`

This script creates or updates content for the GitHub wiki in the `~/punch_card_wiki` directory.

**Usage:**
```bash
./update_wiki.sh
```

**What it does:**
- Creates a `~/punch_card_wiki` directory if it doesn't exist
- Generates a comprehensive Version-History.md file with details of all project versions
- Creates or updates _Sidebar.md for wiki navigation
- Provides instructions for copying content to the GitHub wiki

**Notes:**
- After running this script, you'll need to manually copy the content to your GitHub wiki repository
- See [docs/WIKI_UPDATE_GUIDE.md](../docs/WIKI_UPDATE_GUIDE.md) for detailed instructions

## Adding New Scripts

When adding new scripts to this directory:

1. Make the script executable with `chmod +x scriptname.sh`
2. Add documentation for the script in this README.md
3. Include a comment header in the script explaining its purpose and usage
4. Add any dependencies or requirements to the script documentation

## Best Practices

- Keep scripts modular and focused on a single task
- Include appropriate error handling and user feedback
- Provide clear usage instructions in script headers
- Use consistent coding style and documentation format
- Test scripts thoroughly before committing 