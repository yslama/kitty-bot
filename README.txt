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

1. Clone this repository:

```bash
git clone https://github.com/yourusername/kitty-checker-bot.git
cd kitty-checker-bot
```

2. Install dependencies:

```bash 
pip install -r requirements.txt
```

## Configuration

### Email Setup
1. Create a Gmail App Password:
   - Go to your [Google Account Security Settings](https://myaccount.google.com/security)
   - Enable 2-Step Verification if not already enabled
   - Go to App Passwords (at the bottom of the page)
   - Generate a new app password for "Mail" and your application

2. Set up environment variables:
   Create a `.env` file in the project root with:
   ```
   KITTY_SENDER_EMAIL=your-email@gmail.com
   KITTY_APP_PASSWORD=your-app-password
   KITTY_RECEIVER_EMAIL=recipient@email.com
   ```

   Or set them directly in your terminal:
   ```bash
   # Linux/Mac
   export KITTY_SENDER_EMAIL="your-email@gmail.com"
   export KITTY_APP_PASSWORD="your-app-password"
   export KITTY_RECEIVER_EMAIL="recipient@email.com"
   ```

## Setup

1. Create a `.env` file in the project root with the following variables:
```
KITTY_SENDER_EMAIL=your-email@gmail.com
KITTY_APP_PASSWORD=your-app-password
KITTY_RECEIVER_EMAIL=recipient@email.com
```

## Usage

For local development, run:
```bash
python src/main.py
```

The script will automatically:
- Create a `data` directory and store kitties.csv
- Create a `logs` directory and store kitty_checker.log
- Check for new kittens and send email notifications

## Project Structure

```
kitty-bot/
├── src/
│   ├── main.py           # Entry point and scheduler
│   └── kitty_checker.py  # Core functionality
├── data/                # Created automatically
│   └── kitties.csv      # Database of found kittens
├── logs/               # Log files directory
│   └── kitty_checker.log # Log file
├── .env                # Environment variables (create this)
├── .gitignore          # Git ignore file
├── requirements.txt    # Python dependencies
├── Procfile           # Railway process file
├── runtime.txt        # Python version specification
├── README.txt          # Project documentation
└── LICENSE            # MIT License file
```

## Deployment

This project is configured for Railway deployment. The following files are used:
- `requirements.txt`: Lists all Python dependencies
- `Procfile`: Specifies the command to run the worker
- `runtime.txt`: Specifies the Python version

## Logging
- Logs are written to `kitty_checker.log`
- Contains information about script execution, errors, and new kitten discoveries

## Contributing
Feel free to open issues or submit pull requests if you have suggestions for improvements!

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer
This script is not affiliated with SF SPCA. Please use responsibly and in accordance with SF SPCA's terms of service.