# Template Files

This directory contains template files for configuration that requires sensitive information.

## Usage

1. Copy the desired template file to the appropriate location
2. Rename the file to remove the `.template` extension
3. Replace the placeholder values with your actual credentials

## Available Templates

### `api_keys.json.template`

Template for API keys configuration. Copy this to the `secrets` directory and rename to `api_keys.json`:

```bash
cp templates/api_keys.json.template secrets/api_keys.json
```

Then edit the file to add your actual API keys.

## Security Notice

- Never commit files containing real API keys or credentials to the repository
- All sensitive files should be added to `.gitignore`
- The `secrets` directory is already configured to be ignored by git 