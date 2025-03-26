# IBM Punch Card Display System

A terminal-based simulator of an IBM 80-column punch card display system, featuring LED grid visualization and message processing capabilities.

## Project Structure

```
punch_card_system/
├── src/                    # Source code
│   ├── __init__.py
│   ├── display.py         # Main display system
│   ├── database.py        # Database operations
│   ├── message_generator.py # Message generation (random & OpenAI)
│   ├── punch_card_stats.py # Statistics tracking
│   └── utils.py           # Utility functions
├── config/                 # Configuration files
│   ├── config.yaml        # Main configuration
│   └── credentials.yaml   # API credentials
├── data/                   # Data storage
│   └── messages.db        # SQLite database
├── tests/                  # Test files
│   └── test_display.py
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Features

- Terminal-based IBM 80-column punch card simulation
- LED grid visualization with character-by-character display
- Message processing with punch card encoding
- Statistics tracking and display
- Random sentence generation
- OpenAI API integration for message generation
- Diagnostic logging and system information display
- SQLite database for message storage

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/punch-card-system.git
cd punch-card-system
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure credentials:
   - Copy `config/credentials.yaml.example` to `config/credentials.yaml`
   - Add your OpenAI API key to the credentials file

## Usage

Run the program:
```bash
python src/display.py
```

Command line arguments:
- `--test-message`: Custom test message
- `--led-delay`: Delay between LED updates
- `--message-delay`: Delay between messages
- `--random-delay`: Enable random delays between messages

## Message Processing

The system processes messages in the following order:
1. Test messages (if configured)
2. System diagnostic information (IP address, etc.)
3. Randomly generated sentences
4. OpenAI-generated messages (if configured)

## Database Structure

The SQLite database (`messages.db`) contains:
- `messages` table: Stores all processed messages
- `diagnostics` table: Stores system diagnostic information
- `statistics` table: Stores usage statistics

## Character Encoding

The system uses IBM 026 style punch card encoding:
- A-I: Zone punch row 12 + digit rows 1-9
- J-R: Zone punch row 11 + digit rows 1-9
- S-Z: Zone punch row 0 + digit rows 2-9
- 0-9: Single punch in respective rows
- Special characters: Various combinations of punches

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Version History

- v0.0.1 (2024-03-17): Initial release
  - Basic punch card display
  - Test message support
  - Statistics tracking
  - Random sentence generation
  - OpenAI integration
  - Diagnostic logging 