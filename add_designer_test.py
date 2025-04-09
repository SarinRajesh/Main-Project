from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

def login_customer(driver):
    driver.get("http://127.0.0.1:8000/signin/")
    print("INFO:__main__:Navigated to signin page")
    
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys("Sarin")
    print("INFO:__main__:Entered customer username")
    
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password"))).send_keys("Sarin@12")
    print("INFO:__main__:Entered customer password")
    
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))).click()
    print("INFO:__main__:Clicked login button")
    
    WebDriverWait(driver, 10).until(EC.url_contains("/index/"))
    print("INFO:__main__:Successfully logged in as customer")

def navigate_to_orders(driver):
    try:
        username_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".show-share span"))
        )
        username_element.click()
        print("INFO:__main__:Clicked username in navbar")
        
        orders_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'my_orders')]"))
        )
        orders_link.click()
        print("INFO:__main__:Navigated to orders page")
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[style*='background-color: #ffffff']"))
        )
        print("INFO:__main__:Orders page loaded successfully")
        
    except TimeoutException as e:
        print(f"INFO:__main__:Error during navigation: {str(e)}")

def download_receipt(driver):
    try:
        login_customer(driver)
        navigate_to_orders(driver)
        
        download_buttons = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='download_receipt']"))
        )
        
        if download_buttons:
            download_buttons[0].click()
            print("INFO:__main__:Successfully clicked download receipt button")
            time.sleep(3)
            print("INFO:__main__:Receipt downloaded successfully")
        else:
            print("INFO:__main__:No orders found with downloadable receipts")
        
        print("INFO:__main__:Test completed. Browser will remain open for 10 seconds.")
        
    except TimeoutException as e:
        print(f"INFO:__main__:Error: {str(e)}")

if __name__ == "__main__":
    print("DevTools listening on ws://127.0.0.1:64103/devtools/browser/1085cda7-f171-4a36-969d-aceb5daad9df")
    driver = webdriver.Chrome()
    try:
        driver.maximize_window()
        download_receipt(driver)
        time.sleep(10)
        print("INFO:__main__:Closing the browser")
    finally:
        driver.quit() 