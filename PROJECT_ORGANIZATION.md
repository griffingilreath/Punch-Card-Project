# Punch Card Project Organization

This document outlines the organization of the Punch Card Project codebase.

## Directory Structure

```
punch-card-project/
├── bin/                    # Executable scripts
│   └── punch_card         # Main application entry point
├── .github/            # GitHub workflows and templates
├── assets/             # Static assets and resources
├── backups/            # Important backups (consider gitignoring)
│   └── test_fixes/     # Test fixes from previous versions
├── config/             # Configuration files
│   └── punch_card_settings.json
├── docs/               # Documentation
│   └── versions/       # Version documentation
├── logs/               # Log files (gitignored)
├── release_notes/      # Release notes
├── resources/          # Resource files
├── scripts/            # Utility scripts
│   ├── animation/      # Animation-specific scripts
│   ├── deployment/     # Deployment scripts
│   └── maintenance/    # Maintenance scripts
├── secrets/            # Secret files (gitignored)
├── src/                # Source code
│   ├── animation/      # Animation code
│   ├── api/            # API-related code
│   ├── core/           # Core application code
│   ├── display/        # Display-related code
│   ├── utils/          # Utility functions
│   └── main.py         # Main module
├── tests/              # Test files
│   ├── animation/      # Animation tests
│   ├── api/            # API tests
│   ├── core/           # Core tests
│   └── display/        # Display tests
├── versions/           # Version tracking if needed
├── .gitignore          # Git ignore file
├── CHANGELOG.md        # Changelog
├── README.md           # Project readme
├── requirements.txt    # Python dependencies
└── run.py              # Main entry point script
```

## Main Components

### Source Code (`src/`)

- **animation/**: Contains animation-related code
- **api/**: Contains API integration code
- **core/**: Contains core application logic
- **display/**: Contains UI display code
- **utils/**: Contains utility functions and helpers
- **main.py**: Main application entry point

### Tests (`tests/`)

- Organized by component to mirror the `src/` directory structure
- Each test module corresponds to a source module

### Scripts

- **scripts/animation/**: Animation-specific scripts
- **scripts/deployment/**: Scripts for deployment and release management
- **scripts/maintenance/**: Scripts for maintenance tasks

### Configuration

- Configuration files are stored in the `config/` directory
- Sensitive data should be stored in the `secrets/` directory (gitignored)

### Documentation

- **docs/**: General documentation
- **docs/versions/**: Version-specific documentation
- **release_notes/**: Release notes and change logs

## Entry Points

- **run.py**: Main application entry point
- Use this script to launch the application with appropriate arguments

## Development Guidelines

1. **Maintain Directory Structure**: Follow the established directory structure when adding new files
2. **Keep Modules Focused**: Each module should have a single responsibility
3. **Test Coverage**: Write tests for all functionality
4. **Documentation**: Document all modules, classes, and functions
5. **Configuration**: Keep configuration separate from code

## Version Control

- Use semantic versioning (MAJOR.MINOR.PATCH)
- Document changes in CHANGELOG.md
- Tag releases in git

## Deployment

- Use scripts/deployment for automating the deployment process
- Follow the release checklist in the documentation

## Key Files

- `bin/punch_card`: Main application entry point with command-line options
- `src/core/punch_card.py`: Core application logic
- `src/display/gui_display.py`: GUI implementation
- `src/display/terminal_display.py`: Terminal interface
- `src/utils/version_info.py`: Version information
- `src/animation/animation_manager.py`: Animation system 