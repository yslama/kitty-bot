#!/usr/bin/env python3

import schedule
import time
from kitty_checker import check_cats  # Updated import since files are in same directory
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def job():
    try:
        logging.info("Starting scheduled check")
        check_cats()
        logging.info("Completed scheduled check")
    except Exception as e:
        logging.error(f"Error in scheduled job: {str(e)}")

def main():
    logging.info("Starting kitty checker service")
    
    # Run immediately on startup
    job()
    
    # Then schedule to run every 3 hours
    schedule.every(3).hours.do(job)
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main() 