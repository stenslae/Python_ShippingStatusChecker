import siteScraping
import time

#################TODO: USER UPDATES THIS INFO
inputfile = "orders.csv"
datapath = r"\userpickanyfilepath"
chromedriverpath = r"\pathtochromedriver"
username = r'amazon_email'
password = r'amazon_password'
############################

# Read file and return array with carrier name, tracking number, and row number
data = siteScraping.inforead(inputfile)

#Create txt file to load error info onto
file = open('statusCheckErrors.txt', 'w')

print("Checking shipping statuses...")
#Log into amazon and open webpage to browse for statuses
driver = siteScraping.amazonlogin(username, password, file, datapath, chromedriverpath)

# Check statuses of data
statuses = []
undelivered = []
for i in range(len(data)):
    delivered = siteScraping.checkstatus(data[i][0], data[i][1], data[i][2], file, driver)
    if delivered != None:
        status = [data[i][2], delivered]
        statuses.append(status)
        if 'Delivered' not in delivered:
            undelivered.append(data[i][2])
    else:
        break
    print(f'Row {data[i][2]} has been checked')

# Clear browsing data (history, cookies, cache, etc.)
driver.execute_script("window.localStorage.clear();")
driver.execute_script("window.sessionStorage.clear();")
driver.delete_all_cookies()
driver.quit()

print("All shipping statues have been checked.")
# Load arrays onto csv file to flag undelivered rows, and add row of statuses
siteScraping.infoupdate(inputfile, statuses, undelivered)

print(f"Check updated_{inputfile} for the shipping information and statusCheckErrors.txt for any errors.")
