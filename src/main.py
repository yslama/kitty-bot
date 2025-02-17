#!/usr/bin/env python3

import schedule
import time
from .kitty_checker import check_cats  # Add the dot to indicate relative import
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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
    
    # Run immediately if within business hours
    if is_business_hours():
        job()
    else:
        logging.info("Starting outside business hours, waiting for next business day")
    
    # Schedule to run every 15 minutes
    schedule.every(15).minutes.do(job)
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main() 