# File Organization Guide

## Project Directory Structure

The Punch Card Project is organized as follows:

```
PunchCardProject-Clean/         # Main project directory
├── src/                        # Source code
│   ├── core/                   # Core functionality
│   │   ├── database.py         # Database interactions
│   │   ├── message_database.py # Message database functionality
│   │   ├── message_generator.py# Message generation logic
│   │   └── punch_card.py       # Core punch card functionality
│   ├── display/                # Display modules
│   │   ├── display.py          # Base display class
│   │   ├── display_adapter.py  # Display adapter interface
│   │   ├── gui_display.py      # GUI implementation
│   │   └── terminal_display.py # Terminal interface
│   ├── utils/                  # Utility modules
│   │   ├── gui_integration.py  # GUI integration helpers
│   │   └── settings_menu.py    # Settings functionality
│   └── main.py                 # Main entry point
├── resources/                  # Project resources
│   ├── fonts/                  # Font files
│   ├── images/                 # Image assets
│   └── templates/              # Template files
├── tests/                      # Test modules
├── docs/                       # Documentation
├── run.py                      # Application runner
├── CHANGELOG.md                # Version history
├── README.md                   # Project documentation
├── branch_helper.py            # Branch management script
├── SIMPLIFIED_BRANCH_STRATEGY.md # Branch strategy documentation
├── BRANCH_QUICK_REFERENCE.md   # Git command reference
└── requirements.txt            # Project dependencies
```

## Local Development File Organization

To maintain an organized development environment, follow these guidelines:

### 1. Active Development Files

All active development should happen within the `PunchCardProject-Clean` directory structure. 
This is the canonical source for all code.

### 2. Reference Files

Previous versions and reference implementations are stored in:
- `LOOK HERE Punch Card Project 0.5.3/Punch Card Project/`: Contains version 0.5.3 files
- `Cursor/Punch Card Project/`: Contains the most recent version before cleanup

Only refer to these directories when you need to check previous implementations or recover historical code.
Do not make new changes in these directories.

### 3. Working with Branches

- `main`: Production-ready code - don't modify directly
- `stable`: Pre-release testing - merge from testing when features are complete
- `testing`: Active development - make all new changes here

### 4. Version Management

Version information is tracked in:
- Git tags (e.g., v0.6.1)
- CHANGELOG.md

## File Migration Process

When migrating files from old locations to the clean structure:

1. Identify the files to migrate
2. Copy to the appropriate directory in the clean structure
3. Test functionality
4. Commit to the testing branch
5. Document the migration in CHANGELOG.md

## Guidelines for New Files

When creating new files:

1. Place them in the appropriate directory based on functionality
2. Use consistent naming conventions
3. Add proper imports and package structure
4. Update requirements.txt if new dependencies are added
5. Document the new files in comments and README.md

## Backup Strategy

Backup versions of the project can be found in:
- Git history and tags
- `LOOK HERE Punch Card Project 0.5.3/Punch Card Project/versions/`

For major changes, consider creating a new version tag using:
```bash
./branch_helper.py create-release <version>
``` 