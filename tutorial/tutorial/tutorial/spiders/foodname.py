import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from pathlib import Path
import time
import json
from datetime import datetime, timedelta

class FoodnameSpider(scrapy.Spider):
    name = "foodname"
    # Don't set allowed_domains or start_urls - we'll handle everything with Selenium
    
    def __init__(self):
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        self.logger.info("Setting up Chrome driver...")
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        super().__init__()
    
    def start_requests(self):
        """Override start_requests to avoid HTTP requests, use only Selenium"""
        # Return a dummy request that we'll ignore
        return [scrapy.Request('data:', callback=self.parse_with_selenium)]
    
    def parse_with_selenium(self, response):
        """This method uses Selenium directly, ignoring the Scrapy response"""
        self.logger.info("Using Selenium directly, bypassing Scrapy HTTP...")
        
        try:
            # Load the page
            self.driver.get("https://dineoncampus.com/umassd/whats-on-the-menu")
            time.sleep(10)  # Wait for page to load
            
            self.logger.info(f"Page loaded: {self.driver.title}")
            
            # Save initial page
            self.save_page_content("initial_load")
            
            # Try to find menu data for different dates
            success = self.try_future_dates()
            
            if not success:
                self.logger.warning("No menu data found for any date")
            
        except Exception as e:
            self.logger.error(f"Error in parse: {e}")
        
        finally:
            # Clean up
            self.driver.quit()
    
    def try_future_dates(self):
        """Try different future dates to find menu data"""
        current_date = datetime.now()
        dates_to_try = []
        
        # Generate next 15 weekdays
        days_added = 0
        day_offset = 1
        
        while days_added < 15:
            future_date = current_date + timedelta(days=day_offset)
            if future_date.weekday() < 5:  # Weekdays only
                dates_to_try.append(future_date)
                days_added += 1
            day_offset += 1
        
        self.logger.info(f"Will try {len(dates_to_try)} dates")
        
        for target_date in dates_to_try:
            self.logger.info(f"Trying date: {target_date.strftime('%A, %B %d')}")
            
            try:
                # Try to set the date and check for menu data
                if self.set_date_and_check(target_date):
                    self.logger.info(f"Found menu data for {target_date.strftime('%Y-%m-%d')}")
                    return True
                    
            except Exception as e:
                self.logger.error(f"Error trying date {target_date}: {e}")
                continue
        
        return False
    
    def set_date_and_check(self, target_date):
        """Set a specific date and check if menu data is available"""
        try:
            # For now, let's just save the page content and check manually
            # The date picker interaction is complex, so we'll start simple
            
            # Check current page content
            page_source = self.driver.page_source
            
            # Look for signs of menu data vs "no menu" message
            if "weren't able to find menus" in page_source:
                self.logger.info("No menu message found")
                return False
            
            # Look for potential menu content
            if any(word in page_source.lower() for word in ['breakfast', 'lunch', 'dinner', 'calories', 'nutrition']):
                self.logger.info("Found potential menu content")
                self.save_page_content(f"potential_menu_{target_date.strftime('%Y_%m_%d')}")
                
                # Try to extract food data
                self.extract_food_data(target_date)
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error setting date: {e}")
            return False
    
    def extract_food_data(self, date):
        """Extract food information from the current page"""
        try:
            self.logger.info("Attempting to extract food data...")
            
            # Look for various food-related elements
            food_selectors = [
                "//div[contains(@class, 'menu')]",
                "//div[contains(@class, 'food')]", 
                "//div[contains(@class, 'item')]",
                "//span[contains(text(), 'cal')]",
                "//div[contains(text(), 'calories')]"
            ]
            
            found_elements = []
            
            for selector in food_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        self.logger.info(f"Found {len(elements)} elements with selector: {selector}")
                        for elem in elements[:5]:  # Limit to first 5
                            text = elem.text.strip()
                            if text and len(text) > 3:
                                found_elements.append({
                                    'selector': selector,
                                    'text': text,
                                    'tag': elem.tag_name
                                })
                except Exception as e:
                    self.logger.error(f"Error with selector {selector}: {e}")
            
            # Save findings
            if found_elements:
                findings = {
                    'date': date.strftime('%Y-%m-%d'),
                    'elements_found': len(found_elements),
                    'elements': found_elements
                }
                
                json_filename = f"food_findings_{date.strftime('%Y_%m_%d')}.json"
                with open(json_filename, 'w') as f:
                    json.dump(findings, f, indent=2)
                
                self.logger.info(f"Saved {len(found_elements)} findings to {json_filename}")
            else:
                self.logger.info("No food-related elements found")
                
        except Exception as e:
            self.logger.error(f"Error extracting food data: {e}")
    
    def save_page_content(self, suffix):
        """Save current page content"""
        try:
            html_content = self.driver.page_source
            filename = f"page_{suffix}.html"
            Path(filename).write_text(html_content, encoding='utf-8')
            self.logger.info(f"Saved page to {filename} ({len(html_content)} chars)")
        except Exception as e:
            self.logger.error(f"Error saving page: {e}")
    
    def closed(self, reason):
        """Clean up when spider closes"""
        if hasattr(self, 'driver'):
            try:
                self.driver.quit()
            except:
                pass