# TAKEN FROM ZACHARY ROTHSTEIN'S VERY KIND ED POST
# https://edstem.org/us/courses/51032/discussion/4207840?comment=9704860
# https://people.cs.uchicago.edu/~zrothstein/newSeleniumVMCode.txt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from pyvirtualdisplay import Display

display = Display(visible=0, size=(800, 600))
display.start()

# Set options for headless Chrome
options = Options()
options.add_argument("--headless")  # Run in headless mode
options.add_argument("--no-sandbox")  # Bypass OS security model, necessary for Docker containers
options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems

# Assuming chromedriver is in PATH, otherwise specify the executable path
driver = webdriver.Chrome(options=options)

driver.get("https://www.google.com")

# print out the page title
title = driver.title
print("Visited the page entitled: " + title)

# Wait to load the page
time.sleep(5)

print("\n\nFirst, Blase wants to print out the page's HTML source:")
rawhtml = driver.page_source
print(rawhtml)

print("\n\nNow Blase wants to print out the rendered contents of the page:")
contents = driver.find_element(By.XPATH, "/html/body").text
print(contents)

driver.quit()
display.stop()
