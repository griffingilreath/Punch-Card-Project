# Punch Card Project v0.6.6

## Release Highlights
Version 0.6.6 significantly improves the settings management system with a dedicated `SettingsManager` class and secure keychain integration for API keys.

## Key Changes and Features

### Secure API Key Storage
- API keys are now securely stored in the system keychain
- No more plaintext API keys in the settings file
- Enhanced security for API credentials

### Centralized Settings Management
- New `SettingsManager` class with typed access to all settings
- Simplified access to settings throughout the application
- Improved type safety and validation

### Improved Settings Dialog
- Redesigned settings dialog with a tabbed interface
- Better organization of related settings
- Enhanced visual feedback for API testing
- Made the settings dialog more responsive and user-friendly

### API Integration Improvements
- Better error handling for API connections
- Enhanced status reporting
- More reliable API key validation

## Installation and Requirements

The application requires Python 3.10+ and PyQt6.

```bash
# Clone the repository
git clone https://github.com/your-username/punch-card-project.git

# Navigate to the project directory
cd punch-card-project

# Install dependencies
pip install -r requirements.txt

# Run the application
python punch_card.py
```

## Requirements
- Python 3.10+
- PyQt6
- keyring
- openai
- requests

## Usage
- Run the application with `python punch_card.py`
- For more options, use `python punch_card.py --help`

## Documentation
For more detailed information, see the release notes in the `release_notes` directory.

## License
Copyright © 2023-2024 