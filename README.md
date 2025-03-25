# Punch Card Project

[![Current Version](https://img.shields.io/badge/version-0.6.2-blue.svg)](https://github.com/griffingilreath/Punch-Card-Project/releases/tag/v0.6.2)

A modernized implementation of the IBM 026 punch card system for historical and educational purposes.

## Version History

### v0.6.2 (Current)
- Added support for multiple character encodings
- Improved LED matrix visualization
- Enhanced error handling for hardware integration
- Updated documentation with detailed examples
- Fixed GPIO pin mapping issues
- Resolved character encoding edge cases
- Improved error messages for invalid punch patterns
- Added comprehensive hardware setup guide
- Updated installation instructions
- Expanded troubleshooting section

### v0.6.1
- Implemented secure API key handling
- Added automated testing framework
- Enhanced error reporting
- Improved documentation clarity
- Fixed minor UI bugs

### v0.6.0
- Major UI overhaul with modern design
- Added support for custom encoding schemes
- Integrated OpenAI API for pattern recognition
- Enhanced hardware simulation mode
- Improved performance and stability

### v0.5.3
- Added ASCII art banner
- Implemented basic punch card visualization
- Created initial hardware integration
- Set up project structure and documentation

## Project Overview

This project provides a full GUI implementation of an IBM 026 punch card system, allowing users to experiment with this historical computing technology in a modern environment. It's designed for educational purposes to help understand the foundations of computer programming and data processing.

## Features

- Interactive GUI with authentic IBM 026 layout
- Card visualization and encoding
- Support for multiple character encodings
- Import/export functionality
- Historical reference materials

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Required packages (see requirements.txt)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/griffingilreath/Punch-Card-Project.git
   cd Punch-Card-Project
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python src/main.py
   ```

## Project Structure

- `/src` - Source code for the application
- `/resources` - Images, fonts, and other static resources
- `/docs` - Documentation and historical references
- `/tests` - Unit and integration tests

## Development

This project follows a simplified branching strategy with three main branches:

- `main` - Production-ready code
- `stable` - Pre-release code that has passed testing
- `testing` - Active development branch

For more details, see [SIMPLIFIED_BRANCH_STRATEGY.md](SIMPLIFIED_BRANCH_STRATEGY.md).

Quick reference for common Git operations can be found in [BRANCH_QUICK_REFERENCE.md](BRANCH_QUICK_REFERENCE.md).

## Contributing

We welcome contributions! Please follow these steps:

1. Check out the `testing` branch
2. Make your changes
3. Submit a pull request

Please ensure your code follows our coding standards and includes appropriate tests.

## Version History

**Current Version: 0.6.2** - Restored OpenAI settings and Statistics tabs

See [Releases](https://github.com/griffingilreath/Punch-Card-Project/releases) for all released versions and [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- IBM for the original 026 Keypunch machine
- Various historical references on punch card systems
- All contributors to this project 