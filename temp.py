from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

s = Service(r"C:\My Projects\Advanced Web Scraping\msedgedriver.exe")
driver = webdriver.Edge(service=s)
driver.get("https://new.dineoncampus.com/umassd/whats-on-the-menu/the-grove/2025-06-25/lunch")
# wait for some time to load the website
time.sleep(10)

button_click = driver.find_element(By.XPATH,"/html/body/div/div/div/main/div[1]/div[3]/div/div[2]/div[1]/div[2]/div[2]/table/tbody/tr[1]/td[1]/div[1]/span")
button_click.click()
time.sleep(5)


temp = driver.find_element(By.XPATH, "/html/body/div/div/div/main/div[2]/div/div/div")

text = temp.text
print(text)

with open("output.txt", "w", encoding="utf-8") as file:
    file.write(text)

print("Text saved to output.txt successfully!")

time.sleep(5)

# close the nutrition information window
close_button = driver.find_element(By.XPATH, "/html/body/div/div/div/main/div[2]/div/button[1]").click()
time.sleep(5)

driver.quit()