#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from . import database
import time

load_dotenv()

# Get project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

# Set up logging
log_dir = os.path.join(PROJECT_ROOT, 'logs')
os.makedirs(log_dir, exist_ok=True)

logger = logging.getLogger()

database_url = os.getenv('DATABASE_URL')

def extract_details(facts_text):
    age_match = re.search(r'Age:\s*([\d]{1}) m', facts_text)
    gender_match = re.search(r'Gender:\s*(Male|Female)', facts_text)

    if age_match and gender_match:
        # print(f"Age: {age_match.group(1).strip()}, Gender: {gender_match.group(1).strip()}")
        return int(age_match.group(1).strip()), gender_match.group(1).strip()
    return None, None

def get_age(link):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(link)
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "adoptionFacts__div")))
        
        try:
            facts_element = driver.find_element(By.CLASS_NAME, "adoptionFacts__div")
            facts = facts_element.text
            logger.info(f"Facts: {facts}")
            age, gender = extract_details(facts)
            if age is not None and gender is not None: 
                return age, gender
        except Exception as e:
            logger.error(f"Error finding facts: {str(e)}")
            return None, None
            
    except Exception as e:
        logger.error(f"Error loading page: {str(e)}")
        return None, None
    finally:
        driver.quit()

def send_summary_email(new_cats):
    if not new_cats:
        logger.info("No new cats to report")
        return
        
    # Get email credentials from environment variables
    sender_email = os.environ.get('KITTY_SENDER_EMAIL')
    sender_password = os.environ.get('KITTY_APP_PASSWORD')
    receiver_email = os.environ.get('KITTY_RECEIVER_EMAIL')
    
    if not all([sender_email, sender_password, receiver_email]):
        logger.error("Missing email configuration. Please set KITTY_SENDER_EMAIL, KITTY_APP_PASSWORD, and KITTY_RECEIVER_EMAIL environment variables.")
        return
    
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = f"New Kittens Alert: Found {len(new_cats)} new kittens!"
    
    body = "New kittens found at SF SPCA!\n\n"
    for cat in new_cats:
        body += f"""
                    Name: {cat['name']}
                    Age: {cat['age']} months
                    Gender: {cat['gender']}
                    Link: {cat['link']}
                    ------------------------
                    """
    body += "\nGo check them out!"
    
    message.attach(MIMEText(body, "plain"))
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = message.as_string()
        server.sendmail(sender_email, receiver_email, text)
        logger.info(f"Summary email sent for {len(new_cats)} new kittens!")
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
    finally:
        server.quit()

def check_cats():
    logger.info("=== Starting New Check ===")
    logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    max_retries = 3
    retry_count = 0
    driver = None  # Initialize driver variable
    
    while retry_count < max_retries:
        try:
            # Initialize database
            logger.info("Initializing database...")
            database.init_db()
            logger.info("Database initialized successfully")
            break
        except Exception as e:
            retry_count += 1
            if retry_count == max_retries:
                logger.error(f"Failed to initialize database after {max_retries} attempts: {str(e)}")
                return
            logger.warning(f"Database initialization attempt {retry_count} failed, retrying...")
            time.sleep(5)
    
    try:
        # Log the check process
        logger.info("Opening web browser...")
        new_cats = []
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        logger.info("Setting up Chrome options...")
        driver = webdriver.Chrome(options=options)
        logger.info("Chrome driver initialized successfully")

        logger.info("Navigating to SF SPCA website...")
        driver.get('https://www.sfspca.org/adoptions/cats/')
        logger.info("Website loaded successfully")
        
        wait = WebDriverWait(driver, 15)
        logger.info("Waiting for cat listings to load...")
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "adoption__item")))
        logger.info("Cat listings loaded successfully")
        
        cat_items = driver.find_elements(By.CLASS_NAME, "adoption__item")
        logger.info(f"Found {len(cat_items)} cats on page")
        
        for idx, item in enumerate(cat_items, 1):
            try:
                name_element = item.find_element(By.CLASS_NAME, "adoption__item--name")
                name = name_element.text
                link = name_element.find_element(By.TAG_NAME, "a").get_attribute("href")
                logger.info(f"Processing cat {idx}/{len(cat_items)}: {name}")
                
                # Check if cat already exists in database by link
                if database.cat_exists(link):
                    logger.info(f"Cat {name} already exists in database, skipping")
                    continue
                
                logger.info(f"Checking details for {name}...")
                result = get_age(link)
                
                # Skip if we couldn't get age and gender
                if result is None or result == (None, None):
                    logger.info(f"Skipping {name}: may not be the perfect kitty bro for Miske!")
                    continue
                    
                age, gender = result
                logger.info(f"Found cat: {name}, Age: {age} months, Gender: {gender}")
                
                if age is not None and isinstance(age, (int, float)) and age <= 8 and gender is not None:
                    # Try to add to database
                    if database.add_kitty(name, age, gender, link):
                        new_cats.append({
                            "name": name,
                            "age": age,
                            "gender": gender,
                            "link": link
                        })
                        logger.info(f"Added new cat: {name} ({age} months, {gender})")
                else:
                    logger.info(f'{name} is too old or wrong gender, skipping.')
                
            except Exception as e:
                logger.error(f"Error processing cat {name if 'name' in locals() else 'unknown'}: {str(e)}")

        if new_cats:
            logger.info("Sending email notification...")
            send_summary_email(new_cats)
            logger.info(f"✨ Found {len(new_cats)} new cats!")
            for cat in new_cats:
                logger.info(f"New cat: {cat['name']} ({cat['age']} months)")
        else:
            logger.info("No new cats found this time")
        
        # Display current database contents
        logger.info("Retrieving current database contents...")
        all_cats = database.get_all_kitties()
        logger.info("\nCurrent Database Contents:")
        logger.info("-" * 50)
        for cat in all_cats:
            logger.info(f"Name: {cat.name}")
            logger.info(f"Age: {cat.age} months")
            logger.info(f"Gender: {cat.gender}")
            logger.info(f"Found: {cat.found_at.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"Link: {cat.link}")
            logger.info("-" * 50)
        logger.info(f"Total cats in database: {len(all_cats)}")
        
    except Exception as e:
        logger.error(f"❌ Error during check: {str(e)}", exc_info=True)
    finally:
        if driver:  # Only quit if driver was initialized
            logger.info("Closing Chrome driver...")
            driver.quit()
            logger.info("Chrome driver closed successfully")
        logger.info("=== Check Complete ===\n")

if __name__ == "__main__":
    check_cats() 