# Import Statements
import pandas as pd
import numpy as np
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Logs into Amazon and goes to your orders page
def amazonlogin(username, password, file, custompath, chromedriverpath):
    # Amazon login page
    url = 'https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2Flog%2Fs%3Fk%3Dlog%2Bin%26ref_%3Dnav_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0'

    # Set up Selenium
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-plugins-discovery")
    # chrome_options.add_argument("--headless")  # Can run in headless
    chrome_options.add_argument(f"--user-data-dir={custompath}")

    service = Service(rf'{chromedriverpath}')
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Load the page
        driver.get(url)

        # Wait for the page to load and locate the email input field
        emailenter = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".a-input-text.a-span12.auth-autofocus.auth-required-field"))
        )

        # Enter Username
        emailenter.clear()
        emailenter.send_keys(username)

        # Locate and click the continue button
        continuebutton = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".a-button.a-button-span12.a-button-primary"))
        )
        continuebutton.click()

        # Wait for the password input field to appear
        passwordenter = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".a-input-text.a-span12.auth-required-field"))
        )

        # Enter Password
        passwordenter.clear()
        passwordenter.send_keys(password)

        # Locate and click the sign-in button
        signinbutton = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".a-button.a-button-span12.a-button-primary"))
        )
        signinbutton.click()

        # Check the language of the website
        amazonlanguage = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#icp-nav-flyout"))
        )
        # Change the language of the website
        if 'EN' not in amazonlanguage.text:
            amazonlanguage.click()
            english = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".a-row.a-spacing-mini"))
            )
            english.click()
            confirm = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".a-button.a-spacing-top-mini.a-button-primary"))
            )
            confirm.click()


        # Open your account page
        youraccount = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#nav-link-accountList"))
        )
        youraccount.click()

        # Select your orders
        yourorderscard = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".ya-card-cell"))
        )
        yourorderscard.click()

        # Return the driver after successful login
        return driver

    except Exception as e:
        file.write(f"Unable to log into Amazon: {str(e)}\n")
        driver.quit()
        return None

# Get the status description
def checkstatus(orderyear, row, orderid, file, driver):
    # Check the current date
    current_date = datetime.utcnow()
    parsed_date = datetime.strptime(orderyear, "%Y-%m-%dT%H:%M:%SZ")
    six_months_ago = current_date - relativedelta(months=6)

    # Determine if we can look at the delivery status
    if parsed_date < six_months_ago:
        return None
    else:
        try:
            # Select the year of orders you are looking at
            timecontainer = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "#time-filter"))
            )
            dropdown = Select(timecontainer)
            dropdown.select_by_value(f'year-{orderyear[0:4]}')

            # Wait for the page to load and locate the email input field
            searchbar = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "#searchOrdersInput"))
            )

            # Enter Username
            searchbar.clear()
            searchbar.send_keys(orderid)

            # Enter your search
            enterbutton = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".a-button-input"))
            )
            enterbutton.click()

            # Wait for the parent container to load
            parent = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#ordersContainer"))
            )

            # Once the parent container is loaded, find child elements within it
            childs = parent.find_elements(By.CSS_SELECTOR, '.a-row.shipment-top-row.js-shipment-info-container')
            isblue = False
            result = ""

            for child_element in childs:
                result += child_element.text + ' '
                if not isblue:
                    try:
                        child_element = parent.find_element(By.CSS_SELECTOR, '.a-size-medium.a-color-success.a-text-bold')
                        isblue = True
                    except:
                        isblue = isblue

        except Exception as e:
            file.write(f"Error for row {row}: {str(e)}\n")
            return 'Unknown'

        # Determine if the package was delivered or not (descending priority for multiple packages case)
        if 'Delivered' in result:
            delivered = 'Delivered'
        elif isblue:
            delivered = 'Shipped'
        else:
            delivered = 'Not Shipped'

        driver.back()
        return delivered

# Load arrays onto csv file to flag undelivered rows, and add row of info describing
def infoupdate(filename, statuses, undelivered):
    # Reads original csv file
    df = pd.read_csv(filename)

    # Format arrays to add to DataFrame
    formatstatus = [''] * len(df)
    formatundeliv = [''] * len(df)
    for i in range(len(statuses)):
        if formatstatus[int(statuses[i][0])-2] != '':
            formatstatus[int(statuses[i][0])-2] = formatstatus[int(statuses[i][0])-2] + " and " + statuses[i][1]
        else:
            formatstatus[int(statuses[i][0])-2] = statuses[i][1]
    for i in range(len(undelivered)):
        formatundeliv[int(undelivered[i])-2] = "Yes"

    df['Shipping Status'] = formatstatus
    df['Undelivered?'] = formatundeliv

    # Write updated DataFrame to a new CSV file
    df.to_csv(f'updated_{filename}', index=False)

# Read file and return array with carrier name, tracking number, row number, and order id
def inforead(filename):
    # Reads file and takes important info into a DataFrame
    df = pd.read_csv(filename, usecols=['Order ID', 'Order Date'])

    # Prepare the final array
    final_list = []
    for i in range(len(df)):
        order_id = df.loc[i, 'Order ID']
        order_date = df.loc[i, 'Order Date']
        final_list.append([order_date, i + 2, order_id])

    final = np.array(final_list)

    return final
