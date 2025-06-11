import scrapy
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from pathlib import Path
import time
import json
from datetime import datetime, timedelta

class FoodnameSpider(scrapy.Spider):
    name = "foodname"
    allowed_domains = ["dineoncampus.com"]
    
    def start_requests(self):
        yield SeleniumRequest(
            url="https://dineoncampus.com/umassd/whats-on-the-menu",
            callback=self.parse,
            wait_time=15,
            wait_until=EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    
    def parse(self, response):
        driver = response.meta['driver']
        self.logger.info("Page loaded successfully!")
        
        # Save initial page for reference
        self.save_page_content(driver, "initial_page")
        
        # Try to find a date with menu data
        success = self.try_future_dates(driver)
        
        if not success:
            self.logger.warning("No menu data found for any date tried")
        
        # Close the driver
        driver.quit()
    
    def try_future_dates(self, driver):
        """Try different future dates to find menu data"""
        # Generate weekdays for the next few weeks
        current_date = datetime.now()
        dates_to_try = []
        
        # Try next 20 weekdays (about 4 weeks of weekdays)
        days_added = 0
        day_offset = 1
        
        while days_added < 20:
            future_date = current_date + timedelta(days=day_offset)
            # Monday = 0, Sunday = 6. Try weekdays (0-4)
            if future_date.weekday() < 5:
                dates_to_try.append(future_date)
                days_added += 1
            day_offset += 1
        
        self.logger.info(f"Will try {len(dates_to_try)} dates")
        
        for target_date in dates_to_try:
            self.logger.info(f"Trying date: {target_date.strftime('%A, %B %d, %Y')}")
            
            try:
                # Click on the date picker
                date_picker = driver.find_element(By.ID, "menuDatePicker")
                date_input = date_picker.find_element(By.TAG_NAME, "input")
                date_input.click()
                time.sleep(2)
                
                # Look for calendar popup and navigate to the target date
                if self.navigate_to_date(driver, target_date):
                    time.sleep(3)  # Wait for menu to load
                    
                    # Check if menu data is available
                    if self.check_for_menu_data(driver):
                        self.logger.info(f"Found menu data for {target_date.strftime('%Y-%m-%d')}")
                        self.extract_menu_data(driver, target_date)
                        return True
                    else:
                        self.logger.info(f"No menu data for {target_date.strftime('%Y-%m-%d')}")
                
            except Exception as e:
                self.logger.error(f"Error trying date {target_date}: {e}")
                continue
        
        return False
    
    def navigate_to_date(self, driver, target_date):
        """Navigate the calendar to a specific date"""
        try:
            # Look for calendar elements - this will depend on the calendar implementation
            # For now, we'll try a simple approach
            
            # Look for date buttons in the calendar
            date_text = str(target_date.day)
            
            # Try to find the date button
            date_buttons = driver.find_elements(By.XPATH, f"//button[contains(text(), '{date_text}')]")
            
            if date_buttons:
                date_buttons[0].click()
                return True
            
            # If that doesn't work, try other common calendar selectors
            calendar_dates = driver.find_elements(By.CSS_SELECTOR, ".vc-day-content")
            for date_elem in calendar_dates:
                if date_elem.text == date_text:
                    date_elem.click()
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error navigating to date: {e}")
            return False
    
    def check_for_menu_data(self, driver):
        """Check if menu data is available on the current page"""
        try:
            # Look for the "no menus found" message
            no_menu_elements = driver.find_elements(By.CSS_SELECTOR, ".loading-content_loadingText_22OQi")
            for elem in no_menu_elements:
                if "weren't able to find menus" in elem.text:
                    return False
            
            # Look for positive indicators of menu data
            menu_indicators = [
                ".menu-item",
                ".food-item", 
                "[class*='menu']",
                "[class*='food']",
                ".nutrition",
                ".calories"
            ]
            
            for selector in menu_indicators:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    return True
            
            # Check page text for food-related content
            page_text = driver.page_source.lower()
            food_keywords = ['breakfast', 'lunch', 'dinner', 'calories', 'nutrition', 'serving']
            
            return any(keyword in page_text for keyword in food_keywords)
            
        except Exception as e:
            self.logger.error(f"Error checking for menu data: {e}")
            return False
    
    def extract_menu_data(self, driver, date):
        """Extract food names, calories, and serving sizes from the page"""
        try:
            menu_data = {
                'date': date.strftime('%Y-%m-%d'),
                'location': self.get_current_location(driver),
                'foods': []
            }
            
            # Save the page with menu data
            self.save_page_content(driver, f"menu_data_{date.strftime('%Y_%m_%d')}")
            
            # Try different selectors to find food items
            food_selectors = [
                ".menu-item",
                ".food-item",
                "[class*='menu-item']",
                "[class*='food-item']",
                ".nutrition-item"
            ]
            
            foods_found = []
            
            for selector in food_selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    food_info = self.extract_food_info(element)
                    if food_info:
                        foods_found.append(food_info)
            
            menu_data['foods'] = foods_found
            
            # Save extracted data as JSON
            json_filename = f"menu_data_{date.strftime('%Y_%m_%d')}.json"
            with open(json_filename, 'w') as f:
                json.dump(menu_data, f, indent=2)
            
            self.logger.info(f"Extracted {len(foods_found)} food items and saved to {json_filename}")
            
        except Exception as e:
            self.logger.error(f"Error extracting menu data: {e}")
    
    def extract_food_info(self, element):
        """Extract food name, calories, and serving size from a food element"""
        try:
            food_info = {
                'name': None,
                'calories': None,
                'serving_size': None
            }
            
            # Try to extract food name
            name_selectors = [
                ".food-name", ".menu-item-name", ".item-name", 
                "h3", "h4", ".title", "[class*='name']"
            ]
            
            for selector in name_selectors:
                name_elem = element.find_elements(By.CSS_SELECTOR, selector)
                if name_elem and name_elem[0].text.strip():
                    food_info['name'] = name_elem[0].text.strip()
                    break
            
            # Try to extract calories
            calorie_selectors = [
                ".calories", ".cal", "[class*='calorie']", 
                ".nutrition-calories"
            ]
            
            for selector in calorie_selectors:
                cal_elem = element.find_elements(By.CSS_SELECTOR, selector)
                if cal_elem:
                    cal_text = cal_elem[0].text.strip()
                    # Extract number from text like "250 cal" or "Calories: 250"
                    import re
                    cal_match = re.search(r'(\d+)', cal_text)
                    if cal_match:
                        food_info['calories'] = cal_match.group(1)
                        break
            
            # Try to extract serving size
            serving_selectors = [
                ".serving", ".serving-size", "[class*='serving']",
                ".portion", ".size"
            ]
            
            for selector in serving_selectors:
                serving_elem = element.find_elements(By.CSS_SELECTOR, selector)
                if serving_elem and serving_elem[0].text.strip():
                    food_info['serving_size'] = serving_elem[0].text.strip()
                    break
            
            # Only return if we found at least the name
            if food_info['name']:
                return food_info
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting food info: {e}")
            return None
    
    def get_current_location(self, driver):
        """Get the currently selected dining location"""
        try:
            location_button = driver.find_element(By.CSS_SELECTOR, ".location-name")
            return location_button.text.strip()
        except:
            return "Unknown Location"
    
    def save_page_content(self, driver, suffix):
        """Save the current page content to an HTML file"""
        try:
            html_content = driver.page_source
            filename = f"foodname-{suffix}.html"
            Path(filename).write_text(html_content, encoding='utf-8')
            self.logger.info(f"Saved page content to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving page content: {e}")