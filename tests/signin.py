import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def perform_signin(driver, username, password):
    signin_url = "http://127.0.0.1:8000/signin"
    index_url = "http://127.0.0.1:8000/"
    
    logger.info("Attempting signin...")
    driver.get(signin_url)
    
    try:
        form = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "signin-form"))
        )
        
        form.find_element(By.NAME, "username").send_keys(username)
        form.find_element(By.NAME, "password").send_keys(password)
        form.find_element(By.XPATH, "//button[@type='submit']").click()
        
        # Wait for URL to change
        WebDriverWait(driver, 10).until(EC.url_changes(signin_url))
        
        # Add a small delay to ensure the page has fully loaded
        time.sleep(2)
        
        current_url = driver.current_url
        logger.info(f"Current URL after signin: {current_url}")
        
        if current_url == index_url:
            logger.info("Signin successful: Redirected to index page")
            return True
        else:
            logger.warning("Signin failed: Not redirected to index page")
            return False
    except (TimeoutException, NoSuchElementException) as e:
        logger.error(f"Signin failed: {str(e)}")
        return False

def test_signin():
    logger.info("Starting signin test")
    driver = None
    try:
        driver = webdriver.Chrome()
        driver.maximize_window()
        result = perform_signin(driver, "Sarin", "Sarin@12")
        logger.info(f"Signin test {'passed' if result else 'failed'}")
        
        time.sleep(5)
    finally:
        if driver:
            logger.info("Closing the browser")
            driver.quit()
    logger.info("Signin test completed")

if __name__ == "__main__":
    test_signin()
