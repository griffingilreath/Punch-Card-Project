# Keychain Integration for API Keys

## Overview

Starting with version 0.6.6, the Punch Card Project now securely stores API keys in your system's keychain instead of in plaintext configuration files. This provides several important security benefits:

1. **Improved Security**: API keys are no longer stored in plaintext in settings files
2. **OS-Level Protection**: Keys are stored in your operating system's secure credential storage
3. **Application Isolation**: Only the Punch Card application can access these stored credentials
4. **User-Specific Storage**: Each user has their own secure credential storage

## How It Works

The Punch Card Project uses the `keyring` Python library to interact with your system's native credential storage:

- **macOS**: Keys are stored in the macOS Keychain
- **Windows**: Keys are stored in the Windows Credential Manager
- **Linux**: Keys are stored using the SecretService API (GNOME Keyring/KWallet)

## Using Keychain Integration

### First-Time Setup

When you first enter your API key in the Settings dialog:

1. Open the Settings dialog by clicking the "SETTINGS" button or pressing the 'S' key
2. Navigate to the "API Settings" tab
3. Enter your API key in the "API Key" field
4. Click "Save API Key"

The application will:
- Store the key in your system's keychain
- Remove the key from the settings file
- Show a confirmation message

### Subsequent Usage

After the initial setup:

1. The API key is automatically retrieved from the keychain when needed
2. The settings file only contains a placeholder instead of the actual key
3. The UI will show that a key is configured, but will mask the actual value

### Updating or Removing Keys

To update or remove a stored API key:

1. Open the Settings dialog
2. Navigate to the "API Settings" tab
3. To update: Enter a new API key and click "Save API Key"
4. To remove: Clear the API Key field and click "Save API Key"

## Troubleshooting

If you encounter issues with keychain integration:

### Access Denied

If you receive "Access Denied" errors:
- Your system may prompt you to allow the application access to the keychain
- You may need to run the application with appropriate permissions

### Key Not Found

If your API key seems to be missing:
- Check if the keychain service is running on your system
- Try manually updating the key in the Settings dialog
- Run the update script: `python update_to_v0.6.6.py`

### Migrating from Previous Versions

When upgrading from a previous version:
- The application will automatically migrate your API key to the keychain
- You can also run the update script manually: `python update_to_v0.6.6.py`

## Technical Details

The keychain integration uses:
- Service name: `PunchCardProject_API`
- Username: `openai`
- Password: Your API key

This ensures your API key is correctly isolated from other applications.

## Security Considerations

While keychain integration significantly improves security:
- Your system's security still depends on your user account protection
- Always use a strong password for your user account
- Be cautious about which applications you grant keychain access to 