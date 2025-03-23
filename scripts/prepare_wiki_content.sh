#!/bin/bash

# Prepare Wiki Content for Punch Card Project
# This script will:
# 1. Create a temporary wiki content directory
# 2. Copy research and technical documentation to the wiki directory
# 3. Create necessary wiki pages (Home, Sidebar, etc.)

# Variables
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." &> /dev/null && pwd )"
TEMP_WIKI_DIR="$HOME/punch_card_wiki"

echo "===== Punch Card Project Wiki Content Preparation ====="
echo "This script will prepare content for the GitHub Wiki."
echo "--------------------------------------------"

# Create the temporary wiki directory if it doesn't exist
if [ ! -d "$TEMP_WIKI_DIR" ]; then
    echo "Creating temporary wiki directory at $TEMP_WIKI_DIR..."
    mkdir -p "$TEMP_WIKI_DIR"
else
    echo "Temporary wiki directory already exists at $TEMP_WIKI_DIR"
    echo "Do you want to clear its contents? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo "Clearing temporary wiki directory..."
        rm -rf "$TEMP_WIKI_DIR"/*
    else
        echo "Keeping existing content in the temporary wiki directory."
    fi
fi

# Create essential wiki pages

# Create Home.md if it doesn't exist
if [ ! -f "$TEMP_WIKI_DIR/Home.md" ]; then
    echo "Creating Home.md..."
    cat > "$TEMP_WIKI_DIR/Home.md" << 'EOF'
# Welcome to the Punch Card Project Wiki

This wiki serves as comprehensive documentation for the Punch Card Project, a modern implementation that pays homage to the punch card era of computing through a simulated display system. It combines vintage computing aesthetics with modern technologies like AI-generated content.

## 📖 About This Wiki

This wiki provides detailed information about:

- Historical context of punch cards and their significance
- Technical implementation details of the project
- Design philosophy and research behind the project
- Setup and usage instructions
- Development guidelines and architecture

## 🚀 Quick Start

- [Installation Guide](Installation-Guide) - How to set up the project
- [Usage Examples](Usage-Examples) - Examples of how to use the system
- [API Documentation](API-Documentation) - Technical API documentation

## 🔍 Research & Historical Context

- [Interface Design History](Interface-Design-History) - Research on early computer interface design
- [Punch Card Encoding](Punch-Card-Encoding) - Technical details on punch card character encoding
- [Sociological Aspects](Sociological-Aspects) - The cultural impact of punch cards
- [LED Implementation](LED-Implementation) - Guide to LED matrix implementation
- [Design Language](Design-Language) - Design principles and language of the project

## 🛠️ Developer Resources

- [Project Architecture](Project-Architecture) - Overview of the system architecture
- [Contributing Guidelines](Contributing-Guidelines) - How to contribute to the project
- [Testing](Testing) - Testing guidelines and procedures
- [Easter Eggs](Easter-Eggs) - Hidden features and fun aspects

## 📊 Project Status

Current Version: v0.5.2 - The Reorganization Update

### Recent Updates

- **v0.5.2** (The Reorganization Update): Project structure improvements
- **v0.5.1** (The Documentation Update): Enhanced design language documentation
- **v0.5.0** (The GUI Update): Visual interface improvements
EOF
fi

# Create _Sidebar.md if it doesn't exist
if [ ! -f "$TEMP_WIKI_DIR/_Sidebar.md" ]; then
    echo "Creating _Sidebar.md..."
    cat > "$TEMP_WIKI_DIR/_Sidebar.md" << 'EOF'
# Wiki Navigation

## [Home](Home)

## Getting Started
* [Installation Guide](Installation-Guide)
* [Usage Examples](Usage-Examples)
* [API Documentation](API-Documentation)

## Research & History
* [Interface Design History](Interface-Design-History)
* [Punch Card Encoding](Punch-Card-Encoding)
* [Sociological Aspects](Sociological-Aspects)
* [LED Implementation](LED-Implementation)
* [Design Language](Design-Language)

## Development
* [Project Architecture](Project-Architecture)
* [Contributing Guidelines](Contributing-Guidelines)
* [Testing](Testing)
* [Easter Eggs](Easter-Eggs)

## Versions
* [v0.5.2 - Reorganization](v0.5.2-Reorganization)
* [v0.5.1 - Documentation](v0.5.1-Documentation)
* [v0.5.0 - GUI Update](v0.5.0-GUI-Update)
* [v0.1.0 - Initial Release](v0.1.0-Initial-Release)

## Project Links
* [GitHub Repository](https://github.com/griffingilreath/Punch-Card-Project)
* [Issue Tracker](https://github.com/griffingilreath/Punch-Card-Project/issues)
EOF
fi

# Create _Footer.md if it doesn't exist
if [ ! -f "$TEMP_WIKI_DIR/_Footer.md" ]; then
    echo "Creating _Footer.md..."
    cat > "$TEMP_WIKI_DIR/_Footer.md" << 'EOF'
---

<div align="center">

```
D O   N O T   F O L D   S P I N D L E   O R   M U T I L A T E
```

**Punch Card Project Wiki** | Last updated: March 2024 | [Return to Home](Home)

</div>
EOF
fi

# Copy research documentation
echo "Copying research documentation..."
cp -v "$PROJECT_DIR/docs/research/"*.md "$TEMP_WIKI_DIR/"

# Copy technical documentation
echo "Copying technical documentation..."
if [ -d "$PROJECT_DIR/docs/technical/" ]; then
    cp -v "$PROJECT_DIR/docs/technical/"*.md "$TEMP_WIKI_DIR/" 2>/dev/null || echo "No technical documentation found."
fi

# Copy other documentation
echo "Copying other documentation..."
cp -v "$PROJECT_DIR/docs/"*.md "$TEMP_WIKI_DIR/" 2>/dev/null || echo "No additional documentation found."

# Rename files to match wiki convention (replace underscores with hyphens)
echo "Renaming files to match wiki convention..."
for file in "$TEMP_WIKI_DIR/"*_*.md; do
    if [ -f "$file" ]; then
        newfile=$(echo "$file" | sed 's/_/-/g')
        mv -v "$file" "$newfile"
    fi
done

# Convert all filenames to Title-Case-With-Hyphens.md format
echo "Converting filenames to wiki format..."
for file in "$TEMP_WIKI_DIR/"*.md; do
    if [ -f "$file" ] && [[ $file != *"_"* ]]; then  # Skip files with underscores (already handled)
        filename=$(basename "$file")
        if [[ $filename != "_"* ]]; then  # Skip _Sidebar.md, _Footer.md, etc.
            newname=$(echo "$filename" | sed -E 's/([A-Z])/-\1/g' | sed 's/^-//' | tr '[:upper:]' '[:lower:]')
            # Convert to title case with hyphens
            newname=$(echo "$newname" | sed -E 's/(^|-)([a-z])/\1\u\2/g')
            if [ "$filename" != "$newname" ] && [ "$filename" != "Home.md" ]; then
                mv -v "$file" "$TEMP_WIKI_DIR/$newname"
            fi
        fi
    fi
done

echo "--------------------------------------------"
echo "✅ Wiki content preparation complete!"
echo "Content has been prepared in: $TEMP_WIKI_DIR"
echo "You can now run the setup_github_wiki.sh script to publish it."
echo "--------------------------------------------" 