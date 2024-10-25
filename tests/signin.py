import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def perform_signin(driver):
    url = "http://127.0.0.1:8000/signin"
    logger.info(f"Attempting to connect to {url}")
    
    driver.get(url)
    logger.info("Successfully loaded the page")
    
    # Wait for the form to be present
    try:
        form = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "signin-form"))
        )
        logger.info("Signin form found on the page")
    except TimeoutException:
        logger.error("Timed out waiting for the signin form to load")
        return False

    # Fill out the form
    fields = [
        ("username", "sarin"),
        ("password", "Sarin@12")
    ]

    for field_name, value in fields:
        try:
            input_field = driver.find_element(By.NAME, field_name)
            input_field.send_keys(value)
            logger.info(f"Entered {value} into field with NAME: {field_name}")
        except NoSuchElementException:
            logger.warning(f"Could not find field for: {field_name}")
            return False

    # Find and click the submit button
    try:
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        logger.info("Clicked the submit button")
    except NoSuchElementException:
        logger.error("Could not find the submit button")
        return False

    # Wait to see if we're redirected
    time.sleep(5)
    
    # Log the current URL
    current_url = driver.current_url
    logger.info(f"Current URL after form submission: {current_url}")

    if current_url == "http://127.0.0.1:8000/":
        logger.info("Redirected to home page, checking for login indicators")
        try:
            # Look for the username display in the header
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.show-share span"))
            )
            username_element = driver.find_element(By.CSS_SELECTOR, "div.show-share span")
            if username_element.text.lower() == "sarin":  # Convert to lowercase for comparison
                logger.info("Signin process completed successfully. Username found in header.")
                return True
            else:
                logger.warning(f"Username in header doesn't match. Found: {username_element.text}")
                return False
        except TimeoutException:
            logger.warning("Redirected to home page, but couldn't find login indicators")
            return False

    elif "success" in current_url.lower() or "dashboard" in current_url.lower():
        logger.info("Signin process completed successfully")
        return True
    else:
        logger.warning("Signin process might not have completed as expected")
        return False

def test_signin():
    driver = None
    try:
        # Setup WebDriver (Chrome in this example)
        logger.info("Initializing Chrome WebDriver")
        driver = webdriver.Chrome()
        driver.maximize_window()
        
        if perform_signin(driver):
            logger.info("Signin test passed")
        else:
            logger.error("Signin test failed")

    except WebDriverException as e:
        logger.error(f"WebDriver error: {str(e)}")
    except Exception as e:
        logger.error(f"Signin test failed: {str(e)}")
    finally:
        if driver:
            logger.info("Closing the browser")
            driver.quit()

if __name__ == "__main__":
    test_signin()
