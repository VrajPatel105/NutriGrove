from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from pathlib import Path
import time

print("Testing Selenium directly...")

try:
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    print("Setting up Chrome driver...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    print("Loading website...")
    driver.get("https://dineoncampus.com/umassd/whats-on-the-menu")
    
    time.sleep(10)
    
    print(f"Page title: {driver.title}")
    print(f"Current URL: {driver.current_url}")
    print(f"Page content length: {len(driver.page_source)} characters")
    
    # Save page
    Path("selenium_test_direct.html").write_text(driver.page_source, encoding='utf-8')
    print("SUCCESS: Saved page as selenium_test_direct.html")
    
    driver.quit()
    print("Selenium test completed successfully!")
    
except Exception as e:
    print(f"Selenium test failed: {e}")
    print("Make sure you have Chrome browser installed and try again.")