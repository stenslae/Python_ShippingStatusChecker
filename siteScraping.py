import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def checkstatus(tracking_number):
    url = f'https://www.aftership.com/track/{tracking_number}'

    # Set up Selenium
    chrome_options = Options()

    service = Service(r'C:\Users\stens\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe')  # Path to chromedriver executable
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Load the page
    driver.get(url)

    # Wait for the shadow host element to be present
    try:
        shadow_host = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div#tracking"))
        )
    except:
        print("Shadow host element not found")
        driver.quit()
        exit()

    # Define a function to get the shadow root element using JavaScript
    def expand_shadow_element(element):
        shadow_root = driver.execute_script('return arguments[0].shadowRoot', element)
        return shadow_root

    # Get the shadow root
    shadow_root = expand_shadow_element(shadow_host)

    # Locate the element inside the shadow root
    try:
        tracking_info_element = WebDriverWait(shadow_root, 20).until(
            lambda d: d.find_element(By.CSS_SELECTOR, ".text-xl.flex.font-semibold.flex-shrink-0")
        )
    except:
        print("Tracking info element not found")
        driver.quit()
        exit()

    # Extract the text from the element
    temp = tracking_info_element.text

    # Close the browser
    driver.quit()

    # Determine if package was delivered or not
    delivered = 'Delivered' in temp
    return delivered


def flag_undelivered_orders(data):
   undelivered = []
   for row in data:
       tracking_number, row_num = row
       delivered = checkstatus(tracking_number)
       if not delivered:
           undelivered.append(row_num)
       time.sleep(2)  # Delay between requests to avoid being blocked

   return undelivered
