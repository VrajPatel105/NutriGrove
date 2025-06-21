from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

s = Service(r"C:\My Projects\Advanced Web Scraping\msedgedriver.exe")
driver = webdriver.Edge(service=s)
driver.get("https://new.dineoncampus.com/umassd/whats-on-the-menu")
time.sleep(10)

html = driver.page_source

path = 'new.html'


with open(path, 'w', encoding='utf-8') as f:
    f.write(html)