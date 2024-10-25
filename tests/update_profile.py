import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from signin import perform_signin  # Ensure this import is correct

logger = logging.getLogger(__name__)

def update_profile(driver):
    try:
        # Perform signin before proceeding to update profile
        if not perform_signin(driver):
            logger.error("Signin failed, cannot proceed to update profile")
            return False

        # Navigate to edit profile page
        if not navigate_to_edit_profile(driver):
            logger.error("Failed to navigate to edit profile page")
            return False

        # Fill out the form
        fill_edit_profile_form(driver)

        # Submit the form
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Update Profile')]"))
        )
        submit_button.click()
        logger.info("Clicked 'Update Profile' button")

        # Wait for confirmation or redirection
        WebDriverWait(driver, 10).until(
            EC.url_contains("/profile")  # Assuming it redirects to profile page after update
        )
        logger.info("Profile updated successfully")

        return True

    except TimeoutException as e:
        logger.warning(f"Timeout while updating profile: {str(e)}")
        logger.debug(f"Page source: {driver.page_source}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while updating profile: {str(e)}")

    return False

def navigate_to_edit_profile(driver):
    try:
        # Wait for the username to be visible in the header
        username_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.show-share span"))
        )
        username_element.click()
        logger.info("Clicked on username to open dropdown menu")

        # Wait for the dropdown menu to appear and click on "My Profile"
        profile_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[text()='My Profile']"))
        )
        profile_link.click()
        logger.info("Clicked on 'My Profile' link")

        # Wait for the profile page to load
        WebDriverWait(driver, 10).until(
            EC.url_contains("/profile")
        )
        logger.info(f"Redirected to profile page: {driver.current_url}")

        # Wait for the "Edit Profile" button to be clickable and click it
        edit_profile_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Edit Profile')]"))
        )
        edit_profile_button.click()
        logger.info("Clicked on 'Edit Profile' button")

        # Wait for the edit profile page to load
        WebDriverWait(driver, 10).until(
            EC.url_contains("/edit_profile")
        )
        logger.info(f"Redirected to edit profile page: {driver.current_url}")

        return True

    except TimeoutException as e:
        logger.warning(f"Failed to navigate to edit profile: {str(e)}")
        logger.debug(f"Page source: {driver.page_source}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while navigating to edit profile: {str(e)}")

    return False

def fill_edit_profile_form(driver):
    try:
        # Fill out the form fields
        fields = {
            "name": "Alphin Paul Saji",
            "phone": "9485838439",
            "email": "alphin2002paul@gmail.com",
            "username": "sarin",
            "address": "123 Main St",
            "home_town": "Kodencherry",
            "district": "Kozhikode",
            "state": "Kerala",
            "pincode": "685895"
        }

        for field, value in fields.items():
            input_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, field))
            )
            input_field.clear()
            input_field.send_keys(value)
            logger.info(f"Filled {field} with value: {value}")

        logger.info("Successfully filled out the edit profile form")

    except TimeoutException as e:
        logger.warning(f"Timeout while filling edit profile form: {str(e)}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while filling edit profile form: {str(e)}")

def test_update_profile():
    driver = None
    try:
        # Setup WebDriver (Chrome in this example)
        logger.info("Initializing Chrome WebDriver")
        driver = webdriver.Chrome()
        driver.maximize_window()
        
        if update_profile(driver):
            logger.info("Successfully updated profile")
        else:
            logger.error("Failed to update profile")

        # Keep the browser open for a specific duration
        logger.info("Test completed. Browser will remain open for 10 seconds.")
        time.sleep(10)  # Keep the browser open for 10 seconds

    except WebDriverException as e:
        logger.error(f"WebDriver error: {str(e)}")
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
    finally:
        if driver:
            logger.info("Closing the browser")
            driver.quit()

if __name__ == "__main__":
    test_update_profile()
