#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()  # Add this line after the imports

# Get project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

# Set up logging
log_dir = os.path.join(PROJECT_ROOT, 'logs')
os.makedirs(log_dir, exist_ok=True)  # Create logs directory if it doesn't exist

logging.basicConfig(
    filename=os.path.join(log_dir, 'kitty_checker.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Constants
CAT_PATH = os.path.join(PROJECT_ROOT, "data", "kitties.csv")

def extract_details(facts_text):
    age_match = re.search(r'Age:\s*([\d]{1}) m', facts_text)
    gender_match = re.search(r'Gender:\s*(Male)', facts_text)

    if age_match and gender_match:
        print(f"Age: {age_match.group(1).strip()}, Gender: {gender_match.group(1).strip()}")
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
            age, gender = extract_details(facts)
            if age is not None and gender is not None: 
                return age, gender
        except Exception as e:
            logging.error(f"Error finding facts: {str(e)}")
            return None, None
            
    except Exception as e:
        logging.error(f"Error loading page: {str(e)}")
        return None, None
    finally:
        driver.quit()

def send_summary_email(new_cats):
    if not new_cats:
        logging.info("No new cats to report")
        return
        
    # Get email credentials from environment variables
    sender_email = os.environ.get('KITTY_SENDER_EMAIL')
    sender_password = os.environ.get('KITTY_APP_PASSWORD')
    receiver_email = os.environ.get('KITTY_RECEIVER_EMAIL')
    
    if not all([sender_email, sender_password, receiver_email]):
        logging.error("Missing email configuration. Please set KITTY_SENDER_EMAIL, KITTY_APP_PASSWORD, and KITTY_RECEIVER_EMAIL environment variables.")
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
        logging.info(f"Summary email sent for {len(new_cats)} new kittens!")
    except Exception as e:
        logging.error(f"Error sending email: {str(e)}")
    finally:
        server.quit()

def check_cats():
    logging.info("Starting cat check")
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(CAT_PATH), exist_ok=True)
    
    try:
        cat_df = pd.read_csv(CAT_PATH)
    except FileNotFoundError:
        cat_df = pd.DataFrame(columns=['name', 'link', 'age'])
        
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    new_cats = []

    try:
        logging.info("Checking for new kitties...")
        driver.get('https://www.sfspca.org/adoptions/cats/')
        
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "adoption__item")))
        
        cat_items = driver.find_elements(By.CLASS_NAME, "adoption__item")
        
        for item in cat_items:
            try:
                name_element = item.find_element(By.CLASS_NAME, "adoption__item--name")
                name = name_element.text
                link = name_element.find_element(By.TAG_NAME, "a").get_attribute("href")
                result = get_age(link)
                
                # Skip if we couldn't get age and gender
                if result is None or result == (None, None):
                    logging.info(f"Skipping {name}: not be the perfect kitty bro for Miske!")
                    continue
                    
                age, gender = result

                cat_record = {
                    "name": name,
                    "link": link,
                    "age": age,
                    "gender": gender
                }
                
                if not cat_df[(cat_df['name'] == cat_record['name']) & 
                            (cat_df['link'] == cat_record['link']) & 
                            (cat_df['age'] == cat_record['age']).empty & 
                            (cat_df['gender'] == cat_record['gender'])].empty:
                    logging.info(f'Cat {name} already exists in database')
                else:
                    if age is not None and isinstance(age, (int, float)) and age <= 4:
                        logging.info(f'Adding {name} to database')
                        cat_df.loc[len(cat_df)] = cat_record
                        new_cats.append(cat_record)
                    else:
                        logging.info(f'{name} is too old, skipping.')
                
            except Exception as e:
                logging.error(f"Error processing cat: {str(e)}")

        cat_df.to_csv(CAT_PATH, index=False)
        
        if new_cats:
            send_summary_email(new_cats)
            logging.info(f"Added {len(new_cats)} new cats to the database")
        else:
            logging.info("No new cats to add")
            
    except Exception as e:
        logging.error(f"Error in main process: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    check_cats() 