# Kitty Checker Bot 🐱

A Python script that monitors the SF SPCA website for new kittens and sends email notifications when young kittens (4 months or younger) become available for adoption.

## Features
- 🔍 Automatically monitors SF SPCA's cat adoption page
- 📊 Tracks kittens' names, ages, and adoption links
- 📧 Sends email notifications for new kittens
- 💾 Maintains a CSV database of discovered kittens
- 📝 Includes logging for monitoring and debugging

## Prerequisites
- Python 3.6 or higher
- Chrome browser installed
- Gmail account for sending notifications

## Installation

1. Create a `.env` file in the project root:
```
KITTY_SENDER_EMAIL=your-email@gmail.com
KITTY_APP_PASSWORD=your-app-password
KITTY_RECEIVER_EMAIL=recipient@email.com
DATABASE_URL=postgresql://username@localhost:5432/kitty_db
```

2. Set up PostgreSQL:
```bash
brew install postgresql@15
brew services start postgresql@15
createdb kitty_db
```

3. Install dependencies:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

Run the scheduler:
```bash
python -m src.main
```

Or use CLI commands:
```bash
python -m src.cli check  # Single check
python -m src.cli list   # List kitties
python -m src.cli stats  # Show stats
python -m src.cli recent # Recent kitties
```

## Project Structure

```
kitty-bot/
├── src/
│   ├── __init__.py       # Package identifier
│   ├── main.py           # Scheduler
│   ├── kitty_checker.py  # Core functionality
│   ├── database.py       # Database operations
│   └── cli.py           # Command-line interface
├── logs/                # Log files directory
├── .env                # Environment variables
├── .gitignore          # Git ignore file
├── requirements.txt    # Python dependencies
├── Procfile           # Railway process file
├── runtime.txt        # Python version specification
├── README.txt         # Project documentation
└── LICENSE           # MIT License file
```

## Database Schema

Table: kitties
- id (Primary Key)
- name (String)
- age (Integer)
- gender (String)
- link (String, Unique)
- found_at (DateTime)

## Deployment

1. Add PostgreSQL database on Railway
2. Set environment variables
3. Deploy using Railway CLI or GitHub integration

## Monitoring

- Railway logs: `railway logs`
- CLI stats: `python -m src.cli stats`
- Email notifications for new kitties

## Logging
- Logs are written to `kitty_checker.log`
- Contains information about script execution, errors, and new kitten discoveries

## Contributing
Feel free to open issues or submit pull requests if you have suggestions for improvements!

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer
This script is not affiliated with SF SPCA. Please use responsibly and in accordance with SF SPCA's terms of service.

## CLI Usage

The application provides a command-line interface for various operations:

```bash
# Run a single check for new kittens
python -m src.cli check

# List all kitties in database
python -m src.cli list

# Show statistics
python -m src.cli stats

# Show recent kitties (default: last 7 days)
python -m src.cli recent
python -m src.cli recent --days 14
```

Available Commands:
- `check`: Run a single check for new kittens
- `list`: Show all kitties in the database
- `stats`: Display statistics about found kitties
- `recent`: Show recently found kitties