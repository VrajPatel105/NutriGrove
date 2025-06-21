from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


text = "hii"
text = temp.text

with open("/output.txt", "w", encoding="utf-8") as file:
    file.write(text)