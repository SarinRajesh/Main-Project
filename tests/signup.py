import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_signin():
    driver = None
    try:
        # Setup WebDriver (Chrome in this example)
        logger.info("Initializing Chrome WebDriver")
        driver = webdriver.Chrome()
        driver.maximize_window()
        
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
            return

        # Log the form's HTML for debugging
        logger.info(f"Form HTML: {form.get_attribute('outerHTML')}")

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

        # Find and click the submit button
        try:
            submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()
            logger.info("Clicked the submit button")
        except NoSuchElementException:
            logger.error("Could not find the submit button")

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
                if username_element.text == "sarin":
                    logger.info("Signin process completed successfully. Username found in header.")
                else:
                    logger.warning(f"Username in header doesn't match. Found: {username_element.text}")
                
                # Check for the presence of the logout option in the share wrapper
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.share-wrapper a[href*='logout']"))
                )
                logger.info("Logout option found in the share wrapper.")
                
                logger.info("Signin process completed successfully")

                # Click on the 'Shop' link
                try:
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

                    if "/shop" in current_url:
                        logger.info("Successfully redirected to shop page")
                        
                        # Wait for product items to load
                        try:
                            product_items = WebDriverWait(driver, 10).until(
                                EC.presence_of_all_elements_located((By.CLASS_NAME, "product-cat-mains"))
                            )
                            logger.info(f"Found {len(product_items)} product items on the page")

                            if product_items:
                                # Try to hover over the first product and click its "View" button
                                try:
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
                                    try:
                                        WebDriverWait(driver, 10).until(
                                            EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".show-cart span"), "1")
                                        )
                                        logger.info("Product successfully added to cart")
                                    except TimeoutException:
                                        logger.warning("Couldn't confirm if product was added to cart")

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
                                    WebDriverWait(driver, 10).until(
                                        EC.url_contains("/cart")
                                    )
                                    logger.info(f"Redirected to cart page: {driver.current_url}")

                                except TimeoutException as e:
                                    logger.warning(f"Failed to interact with product or add to cart: {str(e)}")
                                    # Log the page source for debugging
                                    logger.debug(f"Page source: {driver.page_source}")

                            else:
                                logger.warning("No product items found on the page")

                        except TimeoutException:
                            logger.warning("Failed to find product items on the page")
                            # Log the page source for debugging
                            logger.debug(f"Page source: {driver.page_source}")

                    else:
                        logger.warning("Not redirected to shop page as expected")

                except TimeoutException:
                    logger.warning("Failed to find or click 'Shop' link")
                    # Log the page source for debugging
                    logger.debug(f"Page source: {driver.page_source}")

            except TimeoutException:
                logger.warning("Redirected to home page, but couldn't find login indicators")
            
            # Optional: Check if the 'Shop' link is present in the navigation
            try:
                shop_link = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//nav//a[text()='Shop']"))
                )
                logger.info("'Shop' link found in navigation")
            except TimeoutException:
                logger.warning("'Shop' link not found in navigation")

        elif "success" in current_url.lower() or "dashboard" in current_url.lower():
            logger.info("Signin process completed successfully")
        else:
            logger.warning("Signin process might not have completed as expected")

        # Keep the browser open for a few more seconds for manual inspection
        time.sleep(5)

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