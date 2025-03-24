# Project Reorganization Plan

## Current Issues

1. **Scattered Python Files**: Many Python files in the root directory that should be organized into the src structure
2. **Duplicate Files**: Multiple versions of the same file (e.g., punch_card.py, punch_card 2.py)
3. **Console Logs**: Log files in the root directory that should be in a logs directory
4. **Incomplete Versioning**: Some old files not properly archived
5. **README Organization**: README needs better structure with specific mention of design research

## Reorganization Steps

### 1. File Archiving

Files to archive in versions/0.5.2:
- display_ai_haiku.py
- openai_only_display.py
- openai_punch_card.py
- rich_display.py
- gui_display.py
- full_message_display.py
- simple_demo.py
- run_stable_test.py
- direct_led_test.py
- run_test.py
- quick_message.py
- enhanced_punch_card.py
- run_clean_test.py
- Console log files

### 2. File Consolidation

1. **Display Modules**:
   - All display-related functionality should be in src/display/
   - Consolidate similar display files

2. **Core Functionality**:
   - Move all core functionality to src/core/
   - Ensure clean separation of concerns

3. **Utilities**:
   - Move utility functions to src/utils/
   - Create proper module structure with __init__.py files

### 3. Directory Structure

Proposed directory structure:
```
punch_card_project/
├── src/                    # Source code
│   ├── core/               # Core functionality
│   │   ├── punch_card.py   # Main punch card logic
│   │   ├── message_generator.py
│   │   └── database.py
│   ├── display/            # Display modules
│   │   ├── terminal_display.py
│   │   ├── gui_display.py
│   │   └── led_display.py
│   └── utils/              # Utility functions
│       ├── settings.py
│       └── logging.py
├── docs/                   # Documentation
│   ├── research/           # Research documents
│   │   ├── INTERFACE_DESIGN_HISTORY.md
│   │   ├── DESIGN_LANGUAGE.md
│   │   └── ...
│   └── technical/          # Technical documentation
├── tests/                  # Test files
├── config/                 # Configuration files
├── data/                   # Data files
├── logs/                   # Log files
├── scripts/                # Utility scripts
├── versions/               # Archive of previous versions
│   ├── 0.1.0/
│   ├── 0.5.0/
│   ├── 0.5.1/              # Documentation Update
│   └── 0.5.2/              # Current reorganization target
├── secrets/                # API keys (git-ignored)
└── README.md               # Updated README
```

### 4. README Reorganization

Proposed README structure:
1. **Introduction**: Brief project overview
2. **Features**: List of key features
3. **Installation**: How to install
4. **Usage**: How to use
5. **Project Structure**: Overview of directory structure
6. **Design Language**: Brief section on design research with links to docs
7. **Version History**: Chronological version info
8. **Contributing**: How to contribute
9. **License**: License information

### 5. Implementation Order

1. Create necessary directories
2. Move and reorganize files according to new structure
3. Archive old files
4. Update import statements and file references
5. Update README
6. Create proper git tag for v0.5.2

## Notes

- All files should maintain proper import paths
- Code should be tested after reorganization
- Documentation should be updated to reflect new structure
- Git history should be preserved 