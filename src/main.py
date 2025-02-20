#!/usr/bin/env python3

import schedule
import time
from .kitty_checker import check_cats  # Add the dot to indicate relative import
import logging
from datetime import datetime
import sys
import os
from flask import Flask
import threading

# Modified logging setup for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)  # This ensures logs go to Railway
    ]
)

# Create logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Remove any existing handlers
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Add stdout handler
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(stdout_handler)

# Test log
logger.info("Logging system initialized")

app = Flask(__name__)

@app.route('/')
def home():
    return 'Kitty Bot is running! 🐱'

@app.route('/health')
def health():
    return {
        'status': 'running',
        'time': datetime.now().isoformat(),
        'python_version': sys.version
    }

@app.route('/debug/run-check')
def debug_run_check():
    try:
        logging.info("Manual check triggered via debug endpoint")
        job()
        return {
            'status': 'success',
            'message': 'Check completed, see logs for details',
            'time': datetime.now().isoformat()
        }
    except Exception as e:
        logging.error(f"Error in debug check: {str(e)}")
        return {
            'status': 'error',
            'message': str(e),
            'time': datetime.now().isoformat()
        }

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

def is_business_hours():
    """Check if current time is between 9 AM and 6 PM"""
    now = datetime.now()
    return 9 <= now.hour < 18

def job():
    if not is_business_hours():
        logging.info("Outside business hours, skipping check")
        return
        
    try:
        logging.info("Starting scheduled check")
        check_cats()
        logging.info("Completed scheduled check")
    except Exception as e:
        logging.error(f"Error in scheduled job: {str(e)}")

def main():
    logging.info("Starting kitty checker service")
    
    try:
        # Test database connection at startup
        from . import database
        database.init_db()
        logging.info("Database connection verified")
        
        # Schedule to run every 15 minutes
        schedule.every(15).minutes.do(job)
        
        # Run immediately if within business hours
        if is_business_hours():
            job()
        else:
            logging.info("Starting outside business hours, waiting for next business day")
        
        # Start the scheduler in a separate thread
        scheduler_thread = threading.Thread(target=run_scheduler)
        scheduler_thread.start()
        
        # Start Flask app
        port = int(os.getenv("PORT", 8080))
        app.run(host='0.0.0.0', port=port)
            
    except KeyboardInterrupt:
        logging.info("Received keyboard interrupt, shutting down...")
        return
    except Exception as e:
        logging.error(f"Critical error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main() 