import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from signin import perform_signin
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def update_profile(driver):
    try:
        logger.info("Starting profile update process")
        if not perform_signin(driver, "Sarin", "Sarin@12"):
            logger.error("Signin failed")
            return False

        # Navigate to edit profile page
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.show-share span"))
        ).click()
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[text()='My Profile']"))
        ).click()
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Edit Profile')]"))
        ).click()

        # Update profile fields
        fields = {
            "name": "Sarin Rajesh", "phone": "9497449297",
            "email": "sarinkannattuthara@gmail.com", "username": "sarin",
            "address": "123 Main St", "home_town": "Eramalloor",
            "district": "Alappuzha", "state": "Kerala", "pincode": "688537"
        }
        for field, value in fields.items():
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, field))
            )
            element.send_keys(Keys.CONTROL + "a")  # Select all existing text
            element.send_keys(Keys.DELETE)         # Delete the existing text
            element.send_keys(value)               # Enter new value

        # Submit the form
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Update Profile')]"))
        ).click()

        # Wait for redirect to profile page
        WebDriverWait(driver, 10).until(EC.url_contains("/profile"))
        logger.info("Profile updated successfully")
        return True

    except TimeoutException as e:
        logger.error(f"Timeout error: {str(e)}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
    return False

def test_update_profile():
    logger.info("Starting profile update test")
    with webdriver.Chrome() as driver:
        driver.maximize_window()
        result = update_profile(driver)
        logger.info(f"Profile update {'successful' if result else 'failed'}")
        time.sleep(10)
    logger.info("Test completed")

if __name__ == "__main__":
    test_update_profile()
