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

def add_design_to_moodboard(driver):
    try:
        # Perform signin before proceeding
        if not perform_signin(driver):
            logger.error("Signin failed, cannot proceed to add design to mood board")
            return False

        # Click on Mood Boards in navigation
        mood_boards_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[text()='Mood Boards']"))
        )
        mood_boards_link.click()
        logger.info("Clicked on Mood Boards link")

        # Wait for the mood boards list page to load
        WebDriverWait(driver, 10).until(
            EC.url_contains("/mood-boards")
        )
        logger.info("Mood Boards list page loaded")

        # Add a small delay to ensure all elements are loaded
        time.sleep(2)

        # Log the number of mood board links found
        mood_board_links = driver.find_elements(By.CSS_SELECTOR, "a[href^='/mood-board/']")
        logger.info(f"Number of mood board links found: {len(mood_board_links)}")

        if len(mood_board_links) == 0:
            logger.warning("No mood board links found. Page source:")
            logger.warning(driver.page_source)
            return False

        # Try to click on the first mood board link
        try:
            first_mood_board_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href^='/mood-board/']"))
            )
            first_mood_board_link.click()
            logger.info("Clicked on the first mood board link")
        except Exception as e:
            logger.error(f"Failed to click on mood board link: {str(e)}")
            return False

        # Wait for the mood board detail page to load
        try:
            WebDriverWait(driver, 10).until(
                EC.url_contains("/mood-board/")
            )
            logger.info("Mood Board detail page loaded")
        except TimeoutException:
            logger.error("Timed out waiting for mood board detail page to load")
            logger.info(f"Current URL: {driver.current_url}")
            return False

        # Click on Add Design button
        add_design_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add Design')]"))
        )
        add_design_button.click()
        logger.info("Clicked on Add Design button")

        # Wait for the add design page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Add Design to Mood Board')]"))
        )
        logger.info("Add Design page loaded")

        # Click on the first design's Add to Mood Board button
        add_to_moodboard_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".add-item.btn.float-btn"))
        )
        add_to_moodboard_button.click()
        logger.info("Clicked on Add to Mood Board button for the first design")

        # Wait for the success message
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".swal2-popup"))
        )
        logger.info("Success message appeared")

        # Click OK on the success message
        ok_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".swal2-confirm"))
        )
        ok_button.click()
        logger.info("Clicked OK on success message")

        # Wait to be redirected back to the mood board detail page
        WebDriverWait(driver, 10).until(
            EC.url_contains("/mood-board/")
        )
        logger.info("Redirected back to Mood Board detail page")

        return True

    except TimeoutException as e:
        logger.warning(f"Timeout while adding design to mood board: {str(e)}")
        logger.debug(f"Page source: {driver.page_source}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while adding design to mood board: {str(e)}")

    return False

def test_add_design_to_moodboard():
    driver = None
    try:
        # Setup WebDriver (Chrome in this example)
        logger.info("Initializing Chrome WebDriver")
        driver = webdriver.Chrome()
        driver.maximize_window()
        
        if add_design_to_moodboard(driver):
            logger.info("Successfully added design to mood board")
        else:
            logger.error("Failed to add design to mood board")

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
    test_add_design_to_moodboard()
