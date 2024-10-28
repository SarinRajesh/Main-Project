import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from signin import perform_signin
import sys
import os

# Set logging level to WARNING
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Redirect stderr to devnull
stderr = sys.stderr
sys.stderr = open(os.devnull, 'w')

def add_to_cart(driver):
    try:
        if not perform_signin(driver, "Sarin", "Sarin@12"):
            logger.error("Signin failed, cannot proceed to add to cart")
            return

        # Click on the 'Shop' link
        shop_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//nav//a[text()='Shop']"))
        )
        logger.info("'Shop' link found in navigation")
        shop_link.click()
        logger.info("Clicked on 'Shop' link")

        # Wait for a short time to allow any JavaScript to execute
        time.sleep(2)

        # Log the current URL
        current_url = driver.current_url
        logger.info(f"Current URL after clicking 'Shop': {current_url}")

        if "/shop" in driver.current_url:
            logger.info("Successfully redirected to shop page")
            
            # Wait for product items to load
            product_items = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "product-cat-mains"))
            )
            logger.info(f"Found {len(product_items)} product items on the page")

            if product_items:
                # Try to hover over the first product and click its "View" button
                first_product = product_items[0]
                product_name = first_product.find_element(By.XPATH, ".//h4/a").text
                
                # Hover over the product
                actions = ActionChains(driver)
                actions.move_to_element(first_product).perform()
                logger.info(f"Hovered over product: {product_name}")

                # Wait for the "View" button to be present in the DOM
                view_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, ".//a[text()='View']"))
                )
                
                # Use JavaScript to click the "View" button
                driver.execute_script("arguments[0].click();", view_button)
                logger.info(f"Clicked 'View' button for product: {product_name}")

                # Wait for the product page to load
                WebDriverWait(driver, 10).until(
                    EC.url_contains("/product/")
                )
                logger.info(f"Redirected to product page: {driver.current_url}")

                # Wait for the "Add to Cart" button to be clickable
                add_to_cart_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "addToCartBtn"))
                )
                
                # Click the "Add to Cart" button
                driver.execute_script("arguments[0].click();", add_to_cart_button)
                logger.info("Clicked 'Add to Cart' button")

                # Optional: Wait for a confirmation message or cart update
                WebDriverWait(driver, 10).until(
                    EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".show-cart span"), "1")
                )
                logger.info("Product successfully added to cart")

                # Hover over the "Shop" link in the navbar
                shop_link = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//nav//a[text()='Shop']"))
                )
                actions.move_to_element(shop_link).perform()
                logger.info("Hovered over 'Shop' link in navbar")

                # Wait for the "Cart" link to be clickable and click it
                cart_link = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//nav//a[text()='Cart']"))
                )
                cart_link.click()
                logger.info("Clicked on 'Cart' link")

                # Wait for the cart page to load
                WebDriverWait(driver, 20).until(  # Increased wait time
                    EC.url_contains("/cart")
                )
                logger.info(f"Redirected to cart page: {driver.current_url}")

            else:
                logger.warning("No product items found on the page")

        else:
            logger.warning("Not redirected to shop page as expected")

    except TimeoutException as e:
        logger.warning(f"Failed to interact with product or add to cart: {str(e)}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")

def test_add_to_cart():
    driver = None
    try:
        driver = webdriver.Chrome()
        driver.maximize_window()
        
        add_to_cart(driver)

        time.sleep(10)

    except WebDriverException as e:
        logger.error(f"WebDriver error: {str(e)}")
    except Exception as e:
        logger.error(f"Add to cart test failed: {str(e)}")
    finally:
        if driver:
            driver.quit()

# Restore stderr
sys.stderr = stderr

if __name__ == "__main__":
    test_add_to_cart()
