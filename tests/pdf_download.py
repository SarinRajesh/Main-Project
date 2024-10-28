import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options

# Set logging level to ERROR
logging.basicConfig(level=logging.ERROR)
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

        # Find username and password fields
        username_field = form.find_element(By.NAME, "username")
        password_field = form.find_element(By.NAME, "password")

        # Enter "admin" in both fields
        username_field.send_keys("admin")
        password_field.send_keys("admin")
        logger.info("Entered 'admin' in username and password fields")

        # Find and click the submit button
        submit_button = form.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        logger.info("Clicked the submit button")

        # Wait for the page to load after submission
        WebDriverWait(driver, 10).until(
            EC.url_changes(url)
        )
        logger.info("Page loaded after form submission")

        # Add a delay to allow the admin index page to fully load
        time.sleep(3)  # Wait for 3 seconds
        logger.info("Waited for admin index page to load")

        # Click on the "Users Table" link
        users_table_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Users Table"))
        )
        users_table_link.click()
        logger.info("Clicked on 'Users Table' link")

        # Wait for the Users Table page to load
        WebDriverWait(driver, 10).until(
            EC.url_contains("users_table")
        )
        logger.info("Users Table page loaded")

        # Click on the PDF download link
        try:
            pdf_download_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'download=pdf') and contains(@href, 'user_type=customer')]"))
            )
            pdf_download_link.click()
            logger.info("Clicked on PDF download link")

            # Wait for the PDF to generate (adjust the time as needed)
            time.sleep(5)  # Wait for 5 seconds
            logger.info("Waited for PDF download to start")

        except TimeoutException:
            logger.error("Timed out waiting for PDF download link")
            return False
        except NoSuchElementException as e:
            logger.error(f"PDF download link not found: {str(e)}")
            return False

        # Log the current URL
        current_url = driver.current_url
        logger.info(f"Current URL after PDF download attempt: {current_url}")

        # Return True if the process completed without errors
        return True

    except TimeoutException:
        logger.error("Timed out waiting for the signin form to load or submit")
        return False
    except NoSuchElementException as e:
        logger.error(f"Element not found: {str(e)}")
        return False

def test_signin():
    driver = None
    try:
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--ignore-ssl-errors=yes')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        # Initialize Chrome WebDriver with options
        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()
        
        if perform_signin(driver):
            # Keep the browser open for a set time after download
            wait_time = 5
            time.sleep(wait_time)
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    test_signin()
