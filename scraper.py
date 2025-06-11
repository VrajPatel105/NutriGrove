# -*- coding: utf-8 -*-
"""
UMass Dartmouth Dining Menu Scraper
Specifically designed for dineoncampus.com/umassd
Extracts all menu items with nutritional information, calories, and portions
"""

import requests
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import time
import logging
from datetime import datetime, timedelta
import re
import os

class UMassDDiningScraper:
    def __init__(self, headless=True, timeout=30):
        """
        Initialize the UMass Dartmouth dining scraper
        
        Args:
            headless (bool): Run browser in headless mode
            timeout (int): Default timeout for web elements
        """
        self.timeout = timeout
        self.base_url = "https://dineoncampus.com/umassd"
        self.menu_url = f"{self.base_url}/whats-on-the-menu"
        
        # Setup logging
        self.setup_logging()
        
        # Setup browser
        self.setup_driver(headless)
        
        # Session for API calls
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': self.base_url
        })

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('umassd_dining_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def setup_driver(self, headless):
        """Setup Chrome WebDriver"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        
        # Essential Chrome options
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.set_page_load_timeout(self.timeout)
            self.logger.info("Chrome driver initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Chrome driver: {e}")
            raise

    def wait_for_page_load(self, timeout=10):
        """Wait for page to fully load"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            time.sleep(2)  # Additional wait for dynamic content
        except TimeoutException:
            self.logger.warning("Page load timeout, continuing anyway")

    def get_dining_locations(self):
        """
        Get all dining locations available at UMass Dartmouth
        
        Returns:
            list: List of dining locations with their details
        """
        self.logger.info("Getting UMass Dartmouth dining locations")
        
        try:
            self.driver.get(self.menu_url)
            self.wait_for_page_load()
            
            locations = []
            
            # Common selectors for dining locations
            location_selectors = [
                '[data-location-id]',
                '.location-card',
                '.dining-location',
                '.location-tile',
                '.venue-card',
                '.location-item',
                '.dining-venue'
            ]
            
            for selector in location_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        self.logger.info(f"Found {len(elements)} locations with selector: {selector}")
                        
                        for element in elements:
                            location_data = self.extract_location_info(element)
                            if location_data and location_data not in locations:
                                locations.append(location_data)
                        break
                except Exception as e:
                    self.logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            # If no specific location elements found, look for clickable elements with location names
            if not locations:
                self.logger.info("No location elements found, looking for location names in text")
                locations = self.find_locations_by_text()
            
            self.logger.info(f"Found {len(locations)} dining locations")
            return locations
            
        except Exception as e:
            self.logger.error(f"Error getting dining locations: {e}")
            return []

    def extract_location_info(self, element):
        """Extract location information from element"""
        try:
            location_data = {}
            
            # Get location ID
            location_id = (element.get_attribute('data-location-id') or 
                          element.get_attribute('id') or 
                          element.get_attribute('data-id'))
            
            # Get location name
            name_selectors = ['.location-name', '.venue-name', '.name', 'h1', 'h2', 'h3', 'h4']
            name = None
            
            for selector in name_selectors:
                try:
                    name_elem = element.find_element(By.CSS_SELECTOR, selector)
                    name = name_elem.text.strip()
                    if name:
                        break
                except NoSuchElementException:
                    continue
            
            # If no name in child elements, use element text
            if not name:
                name = element.text.strip().split('\n')[0] if element.text.strip() else None
            
            if name and len(name) > 2:
                location_data = {
                    'id': location_id,
                    'name': name,
                    'element': element
                }
                
                return location_data
                
        except Exception as e:
            self.logger.debug(f"Error extracting location info: {e}")
        
        return None

    def find_locations_by_text(self):
        """Find locations by searching for common UMass Dartmouth dining location names"""
        
        # Known UMass Dartmouth dining locations
        known_locations = [
            "The Grove",
            "Campus Center",
            "The Marketplace", 
            "Starbucks",
            "Dunkin'",
            "Birch Grill",
            "Market @ Birch",
            "The Den",
            "Smoothie Bar",
            "Corsair Cafe"
        ]
        
        found_locations = []
        page_text = self.driver.find_element(By.TAG_NAME, 'body').text
        
        for location_name in known_locations:
            if location_name.lower() in page_text.lower():
                found_locations.append({
                    'id': location_name.lower().replace(' ', '_').replace('@', 'at'),
                    'name': location_name,
                    'element': None
                })
        
        return found_locations

    def select_location(self, location):
        """
        Select a specific dining location
        
        Args:
            location (dict): Location information
            
        Returns:
            bool: True if location was successfully selected
        """
        try:
            if location.get('element'):
                # Click on the location element
                element = location['element']
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(1)
                
                try:
                    element.click()
                except:
                    self.driver.execute_script("arguments[0].click();", element)
                
                time.sleep(2)
                return True
            else:
                # Look for location by name
                location_name = location['name']
                
                # Try different ways to find and click the location
                selectors_to_try = [
                    f"//button[contains(text(), '{location_name}')]",
                    f"//div[contains(text(), '{location_name}')]",
                    f"//span[contains(text(), '{location_name}')]",
                    f"//*[contains(text(), '{location_name}') and (@role='button' or name()='button' or @onclick)]"
                ]
                
                for selector in selectors_to_try:
                    try:
                        element = self.driver.find_element(By.XPATH, selector)
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                        time.sleep(1)
                        element.click()
                        time.sleep(2)
                        return True
                    except NoSuchElementException:
                        continue
                
                self.logger.warning(f"Could not find clickable element for location: {location_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error selecting location {location.get('name', 'Unknown')}: {e}")
            return False

    def get_menu_for_date(self, date_str):
        """
        Get menu for a specific date
        
        Args:
            date_str (str): Date in YYYY-MM-DD format
            
        Returns:
            list: List of menu items
        """
        self.logger.info(f"Getting menu for date: {date_str}")
        
        try:
            # Try to find and interact with date picker
            date_selectors = [
                'input[type="date"]',
                '.date-picker',
                '.datepicker',
                '[data-date]',
                '.calendar-input'
            ]
            
            for selector in date_selectors:
                try:
                    date_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                    date_input.clear()
                    date_input.send_keys(date_str)
                    time.sleep(2)
                    break
                except NoSuchElementException:
                    continue
            
            # Wait for menu to load
            time.sleep(3)
            
            # Extract menu items
            menu_items = self.extract_all_menu_items()
            return menu_items
            
        except Exception as e:
            self.logger.error(f"Error getting menu for date {date_str}: {e}")
            return []

    def extract_all_menu_items(self):
        """
        Extract all menu items from the current page
        
        Returns:
            list: List of menu items with nutritional information
        """
        self.logger.info("Extracting menu items from current page")
        
        menu_items = []
        
        # Comprehensive list of menu item selectors
        item_selectors = [
            '.menu-item',
            '.food-item', 
            '.dish-item',
            '.meal-item',
            '.recipe-item',
            '.menu-product',
            '[data-recipe-id]',
            '[data-item-id]',
            '[data-food-id]',
            '.item-card',
            '.food-card',
            '.recipe-card'
        ]
        
        for selector in item_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    self.logger.info(f"Found {len(elements)} items with selector: {selector}")
                    
                    for element in elements:
                        try:
                            item_data = self.extract_menu_item_data(element)
                            if item_data and item_data.get('name'):
                                menu_items.append(item_data)
                        except Exception as e:
                            self.logger.debug(f"Error extracting item: {e}")
                            continue
                    
                    # If we found items with this selector, break
                    if menu_items:
                        break
                        
            except Exception as e:
                self.logger.debug(f"Selector {selector} failed: {e}")
                continue
        
        # Remove duplicates based on name
        unique_items = []
        seen_names = set()
        
        for item in menu_items:
            name = item.get('name', '').lower()
            if name and name not in seen_names:
                unique_items.append(item)
                seen_names.add(name)
        
        self.logger.info(f"Extracted {len(unique_items)} unique menu items")
        return unique_items

    def extract_menu_item_data(self, element):
        """
        Extract comprehensive data from a menu item element
        
        Args:
            element: Selenium WebElement
            
        Returns:
            dict: Menu item data with nutritional information
        """
        item_data = {
            'name': '',
            'description': '',
            'category': '',
            'price': '',
            'portion_size': '',
            'nutrition': {}
        }
        
        try:
            # Extract name
            name_selectors = [
                '.recipe-name', '.item-name', '.food-name', '.dish-name',
                '.meal-name', '.name', '.title', 'h1', 'h2', 'h3', 'h4', 'h5'
            ]
            
            for selector in name_selectors:
                try:
                    name_elem = element.find_element(By.CSS_SELECTOR, selector)
                    name = name_elem.text.strip()
                    if name and len(name) > 2:
                        item_data['name'] = name
                        break
                except NoSuchElementException:
                    continue
            
            # If no name found, use element text
            if not item_data['name']:
                text_lines = element.text.strip().split('\n')
                for line in text_lines:
                    line = line.strip()
                    if line and len(line) > 2 and not any(char.isdigit() for char in line[:3]):
                        item_data['name'] = line
                        break
            
            # Extract description
            desc_selectors = [
                '.description', '.item-description', '.recipe-description',
                '.ingredients', '.details', 'p'
            ]
            
            for selector in desc_selectors:
                try:
                    desc_elem = element.find_element(By.CSS_SELECTOR, selector)
                    desc = desc_elem.text.strip()
                    if desc and desc != item_data['name']:
                        item_data['description'] = desc
                        break
                except NoSuchElementException:
                    continue
            
            # Extract nutritional information
            nutrition_data = self.extract_nutrition_info(element)
            item_data['nutrition'] = nutrition_data
            
            # Extract price if available
            price_pattern = r'\$(\d+(?:\.\d{2})?)'
            element_text = element.text
            price_match = re.search(price_pattern, element_text)
            if price_match:
                item_data['price'] = f"${price_match.group(1)}"
            
            # Extract portion size
            portion_patterns = [
                r'(\d+(?:\.\d+)?\s*(?:oz|g|ml|lb|kg))',
                r'serves?\s*(\d+)',
                r'(\d+\s*piece[s]?)',
                r'(\d+\s*slice[s]?)'
            ]
            
            for pattern in portion_patterns:
                match = re.search(pattern, element_text, re.IGNORECASE)
                if match:
                    item_data['portion_size'] = match.group(1)
                    break
            
            return item_data
            
        except Exception as e:
            self.logger.debug(f"Error extracting menu item data: {e}")
            return None

    def extract_nutrition_info(self, element):
        """
        Extract nutritional information from menu item element
        
        Args:
            element: Selenium WebElement
            
        Returns:
            dict: Nutritional information
        """
        nutrition_data = {}
        
        try:
            # First try to find and click nutrition button
            nutrition_buttons = [
                '.nutrition-btn', '.nutrition-info', '.nutrition-button',
                '.nutritional-facts', '.nutrition-facts', '.info-btn',
                'button[data-nutrition]', 'button[title*="nutrition"]',
                '[aria-label*="nutrition"]'
            ]
            
            for selector in nutrition_buttons:
                try:
                    nutrition_btn = element.find_element(By.CSS_SELECTOR, selector)
                    if nutrition_btn.is_displayed():
                        # Click to open nutrition info
                        self.driver.execute_script("arguments[0].click();", nutrition_btn)
                        time.sleep(2)
                        
                        # Extract from modal/popup
                        modal_nutrition = self.extract_nutrition_from_modal()
                        if modal_nutrition:
                            nutrition_data.update(modal_nutrition)
                            
                            # Close modal
                            self.close_nutrition_modal()
                            break
                except NoSuchElementException:
                    continue
            
            # Extract nutrition info from element text
            text_nutrition = self.extract_nutrition_from_text(element.text)
            nutrition_data.update(text_nutrition)
            
            # Look for allergen and dietary information
            dietary_info = self.extract_dietary_info(element.text)
            nutrition_data.update(dietary_info)
            
        except Exception as e:
            self.logger.debug(f"Error extracting nutrition info: {e}")
        
        return nutrition_data

    def extract_nutrition_from_modal(self):
        """Extract nutrition data from modal/popup"""
        nutrition_data = {}
        
        try:
            # Wait for modal to appear
            modal_selectors = [
                '.nutrition-modal', '.modal', '.popup', '.nutrition-popup',
                '.nutritional-information', '.nutrition-facts'
            ]
            
            modal_element = None
            for selector in modal_selectors:
                try:
                    modal_element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if modal_element.is_displayed():
                        break
                except TimeoutException:
                    continue
            
            if modal_element:
                modal_text = modal_element.text
                nutrition_data = self.extract_nutrition_from_text(modal_text)
                
        except Exception as e:
            self.logger.debug(f"Error extracting from modal: {e}")
        
        return nutrition_data

    def extract_nutrition_from_text(self, text):
        """Extract nutrition data from text using regex patterns"""
        nutrition_data = {}
        
        # Comprehensive nutrition patterns
        patterns = {
            'calories': [
                r'(\d+)\s*calories?',
                r'calories?[:\s]*(\d+)',
                r'(\d+)\s*cal\b',
                r'cal[:\s]*(\d+)'
            ],
            'calories_from_fat': [
                r'calories from fat[:\s]*(\d+)',
                r'fat calories[:\s]*(\d+)'
            ],
            'total_fat': [
                r'total fat[:\s]*(\d+(?:\.\d+)?)\s*g',
                r'fat[:\s]*(\d+(?:\.\d+)?)\s*g'
            ],
            'saturated_fat': [
                r'saturated fat[:\s]*(\d+(?:\.\d+)?)\s*g'
            ],
            'trans_fat': [
                r'trans fat[:\s]*(\d+(?:\.\d+)?)\s*g'
            ],
            'cholesterol': [
                r'cholesterol[:\s]*(\d+(?:\.\d+)?)\s*mg'
            ],
            'sodium': [
                r'sodium[:\s]*(\d+(?:\.\d+)?)\s*mg'
            ],
            'total_carbs': [
                r'total carbohydrate[s]?[:\s]*(\d+(?:\.\d+)?)\s*g',
                r'carb[s]?[:\s]*(\d+(?:\.\d+)?)\s*g'
            ],
            'dietary_fiber': [
                r'dietary fiber[:\s]*(\d+(?:\.\d+)?)\s*g',
                r'fiber[:\s]*(\d+(?:\.\d+)?)\s*g'
            ],
            'sugars': [
                r'total sugars?[:\s]*(\d+(?:\.\d+)?)\s*g',
                r'sugars?[:\s]*(\d+(?:\.\d+)?)\s*g'
            ],
            'protein': [
                r'protein[:\s]*(\d+(?:\.\d+)?)\s*g'
            ],
            'vitamin_a': [
                r'vitamin a[:\s]*(\d+(?:\.\d+)?)\s*(?:iu|%|mcg)'
            ],
            'vitamin_c': [
                r'vitamin c[:\s]*(\d+(?:\.\d+)?)\s*(?:mg|%)'
            ],
            'calcium': [
                r'calcium[:\s]*(\d+(?:\.\d+)?)\s*(?:mg|%)'
            ],
            'iron': [
                r'iron[:\s]*(\d+(?:\.\d+)?)\s*(?:mg|%)'
            ]
        }
        
        text_lower = text.lower()
        
        for nutrient, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, text_lower)
                if match:
                    try:
                        value = float(match.group(1))
                        nutrition_data[nutrient] = value
                        break
                    except (ValueError, IndexError):
                        continue
        
        return nutrition_data

    def extract_dietary_info(self, text):
        """Extract dietary and allergen information"""
        dietary_data = {}
        
        text_lower = text.lower()
        
        # Dietary preferences
        dietary_indicators = {
            'vegetarian': ['vegetarian', 'veggie'],
            'vegan': ['vegan'],
            'gluten_free': ['gluten free', 'gluten-free', 'gf'],
            'dairy_free': ['dairy free', 'dairy-free'],
            'halal': ['halal'],
            'kosher': ['kosher'],
            'organic': ['organic'],
            'local': ['local', 'locally sourced']
        }
        
        dietary_preferences = []
        for preference, indicators in dietary_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                dietary_preferences.append(preference)
        
        if dietary_preferences:
            dietary_data['dietary_preferences'] = dietary_preferences
        
        # Common allergens
        allergen_indicators = {
            'milk': ['milk', 'dairy'],
            'eggs': ['egg', 'eggs'],
            'fish': ['fish'],
            'shellfish': ['shellfish', 'shrimp', 'crab', 'lobster'],
            'tree_nuts': ['tree nuts', 'nuts', 'almond', 'walnut', 'pecan'],
            'peanuts': ['peanut', 'peanuts'],
            'wheat': ['wheat', 'gluten'],
            'soy': ['soy', 'soybean']
        }
        
        allergens = []
        for allergen, indicators in allergen_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                allergens.append(allergen)
        
        if allergens:
            dietary_data['allergens'] = allergens
        
        return dietary_data

    def close_nutrition_modal(self):
        """Close nutrition modal/popup"""
        try:
            close_selectors = [
                '.close', '.modal-close', '[aria-label="Close"]',
                '.btn-close', 'button:contains("×")', '.x-btn',
                '[data-dismiss="modal"]'
            ]
            
            for selector in close_selectors:
                try:
                    close_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if close_btn.is_displayed():
                        close_btn.click()
                        time.sleep(1)
                        return
                except NoSuchElementException:
                    continue
            
            # Press Escape key as fallback
            self.driver.find_element(By.TAG_NAME, 'body').send_keys('\ue00c')
            time.sleep(1)
            
        except Exception as e:
            self.logger.debug(f"Error closing modal: {e}")

    def scrape_all_menus(self, days_ahead=3):
        """
        Scrape all menus for UMass Dartmouth dining locations
        
        Args:
            days_ahead (int): Number of days ahead to scrape (including today)
            
        Returns:
            dict: Complete menu data
        """
        self.logger.info(f"Starting comprehensive menu scrape for UMass Dartmouth")
        
        # Generate date range
        date_range = []
        for i in range(days_ahead):
            date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
            date_range.append(date)
        
        complete_data = {
            'university': 'UMass Dartmouth',
            'scrape_timestamp': datetime.now().isoformat(),
            'date_range': date_range,
            'menu_data': {}
        }
        
        try:
            # Navigate to menu page
            self.driver.get(self.menu_url)
            self.wait_for_page_load()
            
            # Get all dining locations
            locations = self.get_dining_locations()
            
            if not locations:
                self.logger.warning("No dining locations found, trying to scrape current page")
                # Try to scrape whatever is currently visible
                for date in date_range:
                    menu_items = self.extract_all_menu_items()
                    if menu_items:
                        complete_data['menu_data'][f'Unknown_Location_{date}'] = {
                            'date': date,
                            'location': 'Unknown Location',
                            'menu_items': menu_items
                        }
                return complete_data
            
            # Scrape each location for each date
            for location in locations:
                location_name = location['name']
                self.logger.info(f"Scraping location: {location_name}")
                
                complete_data['menu_data'][location_name] = {}
                
                # Select the location
                if self.select_location(location):
                    # Scrape each date
                    for date in date_range:
                        self.logger.info(f"Scraping {location_name} for {date}")
                        
                        menu_items = self.get_menu_for_date(date)
                        
                        complete_data['menu_data'][location_name][date] = {
                            'date': date,
                            'location': location_name,
                            'menu_items': menu_items
                        }
                        
                        time.sleep(1)  # Be respectful to the server
                else:
                    self.logger.warning(f"Could not select location: {location_name}")
        
        except Exception as e:
            self.logger.error(f"Error in scrape_all_menus: {e}")
        
        # Calculate total items scraped
        total_items = sum(
            len(menu_data.get('menu_items', []))
            for location_data in complete_data['menu_data'].values()
            for menu_data in (location_data.values() if isinstance(location_data, dict) else [location_data])
        )
        
        self.logger.info(f"Scraping completed. Total items: {total_items}")
        complete_data['total_items_scraped'] = total_items
        
        return complete_data

    def save_data(self, data, filename=None):
        """
        Save scraped data in multiple formats
        
        Args:
            data (dict): Complete menu data
            filename (str): Base filename (without extension)
            
        Returns:
            list: List of saved file paths
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"umassd_dining_menu_{timestamp}"
        
        saved_files = []
        
        try:
            # Save as JSON
            json_file = f"{filename}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            saved_files.append(json_file)
            
            # Create detailed CSV
            csv_data = []
            
            for location_name, location_data in data.get('menu_data', {}).items():
                if isinstance(location_data, dict):
                    for date, menu_data in location_data.items():
                        if isinstance(menu_data, dict) and 'menu_items' in menu_data:
                            for item in menu_data['menu_items']:
                                row = {
                                    'scrape_timestamp': data.get('scrape_timestamp', ''),
                                    'university': 'UMass Dartmouth',
                                    'location': location_name,
                                    'date': date,
                                    'item_name': item.get('name', ''),
                                    'description': item.get('description', ''),
                                    'category': item.get('category', ''),
                                    'price': item.get('price', ''),
                                    'portion_size': item.get('portion_size', ''),
                                }
                                
                                # Add comprehensive nutrition data
                                nutrition = item.get('nutrition', {})
                                
                                # Main macronutrients
                                row.update({
                                    'calories': nutrition.get('calories', ''),
                                    'calories_from_fat': nutrition.get('calories_from_fat', ''),
                                    'total_fat_g': nutrition.get('total_fat', ''),
                                    'saturated_fat_g': nutrition.get('saturated_fat', ''),
                                    'trans_fat_g': nutrition.get('trans_fat', ''),
                                    'cholesterol_mg': nutrition.get('cholesterol', ''),
                                    'sodium_mg': nutrition.get('sodium', ''),
                                    'total_carbs_g': nutrition.get('total_carbs', ''),
                                    'dietary_fiber_g': nutrition.get('dietary_fiber', ''),
                                    'sugars_g': nutrition.get('sugars', ''),
                                    'protein_g': nutrition.get('protein', ''),
                                    'vitamin_a': nutrition.get('vitamin_a', ''),
                                    'vitamin_c': nutrition.get('vitamin_c', ''),
                                    'calcium': nutrition.get('calcium', ''),
                                    'iron': nutrition.get('iron', ''),
                                })
                                
                                # Dietary information
                                dietary_preferences = nutrition.get('dietary_preferences', [])
                                allergens = nutrition.get('allergens', [])
                                
                                row.update({
                                    'dietary_preferences': ', '.join(dietary_preferences) if dietary_preferences else '',
                                    'allergens': ', '.join(allergens) if allergens else '',
                                    'is_vegetarian': 'Yes' if 'vegetarian' in dietary_preferences else 'No',
                                    'is_vegan': 'Yes' if 'vegan' in dietary_preferences else 'No',
                                    'is_gluten_free': 'Yes' if 'gluten_free' in dietary_preferences else 'No',
                                    'contains_dairy': 'Yes' if 'milk' in allergens else 'No',
                                    'contains_nuts': 'Yes' if any('nut' in allergen for allergen in allergens) else 'No',
                                })
                                
                                csv_data.append(row)
            
            # Save CSV
            if csv_data:
                csv_file = f"{filename}.csv"
                df = pd.DataFrame(csv_data)
                df.to_csv(csv_file, index=False, encoding='utf-8')
                saved_files.append(csv_file)
            
            # Save Excel with multiple sheets
            if csv_data:
                excel_file = f"{filename}.xlsx"
                with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                    # Main data sheet
                    df.to_excel(writer, sheet_name='Menu_Items', index=False)
                    
                    # Summary sheet
                    if not df.empty:
                        summary_data = []
                        for location in df['location'].unique():
                            location_df = df[df['location'] == location]
                            for date in location_df['date'].unique():
                                date_df = location_df[location_df['date'] == date]
                                summary_data.append({
                                    'location': location,
                                    'date': date,
                                    'total_items': len(date_df),
                                    'avg_calories': date_df['calories'].mean() if 'calories' in date_df.columns else 0,
                                    'vegetarian_options': len(date_df[date_df['is_vegetarian'] == 'Yes']),
                                    'vegan_options': len(date_df[date_df['is_vegan'] == 'Yes']),
                                    'gluten_free_options': len(date_df[date_df['is_gluten_free'] == 'Yes'])
                                })
                        
                        summary_df = pd.DataFrame(summary_data)
                        summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                saved_files.append(excel_file)
            
            # Save summary report
            summary_file = f"{filename}_summary.txt"
            self.save_summary_report(data, summary_file)
            saved_files.append(summary_file)
            
            self.logger.info(f"Data saved to files: {', '.join(saved_files)}")
            
        except Exception as e:
            self.logger.error(f"Error saving data: {e}")
        
        return saved_files

    def save_summary_report(self, data, filename):
        """Save a human-readable summary report"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("UMASSD DINING MENU SCRAPING REPORT\n")
                f.write("=" * 50 + "\n\n")
                
                f.write(f"University: {data.get('university', 'UMass Dartmouth')}\n")
                f.write(f"Scrape Timestamp: {data.get('scrape_timestamp', 'N/A')}\n")
                f.write(f"Date Range: {', '.join(data.get('date_range', []))}\n")
                f.write(f"Total Items Scraped: {data.get('total_items_scraped', 0)}\n\n")
                
                menu_data = data.get('menu_data', {})
                f.write(f"Dining Locations Found: {len(menu_data)}\n\n")
                
                for location_name, location_data in menu_data.items():
                    f.write(f"Location: {location_name}\n")
                    f.write("-" * 30 + "\n")
                    
                    if isinstance(location_data, dict):
                        for date, menu_info in location_data.items():
                            if isinstance(menu_info, dict):
                                items_count = len(menu_info.get('menu_items', []))
                                f.write(f"  {date}: {items_count} menu items\n")
                                
                                # Show sample items
                                sample_items = menu_info.get('menu_items', [])[:3]
                                for item in sample_items:
                                    name = item.get('name', 'Unknown')
                                    calories = item.get('nutrition', {}).get('calories', 'N/A')
                                    f.write(f"    - {name} ({calories} cal)\n")
                    
                    f.write("\n")
                
        except Exception as e:
            self.logger.error(f"Error creating summary report: {e}")

    def debug_current_page(self):
        """Debug what's currently visible on the page"""
        try:
            self.logger.info("=== PAGE DEBUG INFO ===")
            self.logger.info(f"Current URL: {self.driver.current_url}")
            self.logger.info(f"Page Title: {self.driver.title}")
            
            # Check page content
            body = self.driver.find_element(By.TAG_NAME, 'body')
            page_text = body.text[:500]
            self.logger.info(f"Page Text Sample: {page_text}")
            
            # Count elements
            elements_count = {
                'divs': len(self.driver.find_elements(By.TAG_NAME, 'div')),
                'buttons': len(self.driver.find_elements(By.TAG_NAME, 'button')),
                'links': len(self.driver.find_elements(By.TAG_NAME, 'a')),
                'inputs': len(self.driver.find_elements(By.TAG_NAME, 'input')),
            }
            
            for elem_type, count in elements_count.items():
                self.logger.info(f"{elem_type.capitalize()}: {count}")
            
            # Save screenshot
            screenshot_path = f"debug_umassd_{int(time.time())}.png"
            self.driver.save_screenshot(screenshot_path)
            self.logger.info(f"Screenshot saved: {screenshot_path}")
            
        except Exception as e:
            self.logger.error(f"Error in debug: {e}")

    def close(self):
        """Clean up resources"""
        try:
            if hasattr(self, 'driver'):
                self.driver.quit()
            if hasattr(self, 'session'):
                self.session.close()
        except Exception as e:
            self.logger.error(f"Error closing resources: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def main():
    """Main function to run the UMass Dartmouth dining scraper"""
    print("🍽️ UMass Dartmouth Dining Menu Scraper")
    print("=" * 50)
    
    try:
        with UMassDDiningScraper(headless=True, timeout=30) as scraper:
            print("🔍 Starting menu scrape...")
            
            # Scrape menus for the next 3 days
            menu_data = scraper.scrape_all_menus(days_ahead=3)
            
            if menu_data:
                print(f"✅ Scraping completed!")
                print(f"📊 Total items found: {menu_data.get('total_items_scraped', 0)}")
                
                # Save data
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                saved_files = scraper.save_data(menu_data, f"umassd_menu_{timestamp}")
                
                print(f"📁 Files saved:")
                for file_path in saved_files:
                    print(f"   - {file_path}")
                
                # Show summary
                menu_data_dict = menu_data.get('menu_data', {})
                print(f"\n📋 Summary:")
                print(f"   Locations scraped: {len(menu_data_dict)}")
                
                for location, data in menu_data_dict.items():
                    if isinstance(data, dict):
                        dates = list(data.keys())
                        total_items = sum(len(d.get('menu_items', [])) for d in data.values() if isinstance(d, dict))
                        print(f"   {location}: {total_items} items across {len(dates)} dates")
                
            else:
                print("❌ No menu data found")
                
    except KeyboardInterrupt:
        print("\n⚠️ Scraping interrupted by user")
    except Exception as e:
        print(f"💥 Error during scraping: {e}")
        import traceback
        traceback.print_exc()


def debug_mode():
    """Run in debug mode to see what's happening"""
    print("🐛 Debug Mode - UMass Dartmouth Dining")
    print("=" * 50)
    
    try:
        with UMassDDiningScraper(headless=False, timeout=30) as scraper:  # headless=False to see browser
            print("🌐 Navigating to UMass Dartmouth dining page...")
            scraper.driver.get(scraper.menu_url)
            scraper.wait_for_page_load()
            
            # Run debug analysis
            scraper.debug_current_page()
            
            # Try to find locations
            print("\n🏢 Looking for dining locations...")
            locations = scraper.get_dining_locations()
            
            if locations:
                print(f"✅ Found {len(locations)} locations:")
                for loc in locations:
                    print(f"   - {loc['name']} (ID: {loc.get('id', 'N/A')})")
            else:
                print("❌ No locations found")
            
            # Try to extract menu items from current page
            print("\n🍽️ Trying to extract menu items...")
            menu_items = scraper.extract_all_menu_items()
            
            if menu_items:
                print(f"✅ Found {len(menu_items)} menu items:")
                for i, item in enumerate(menu_items[:5]):  # Show first 5
                    name = item.get('name', 'Unknown')
                    calories = item.get('nutrition', {}).get('calories', 'N/A')
                    print(f"   {i+1}. {name} - {calories} calories")
                
                if len(menu_items) > 5:
                    print(f"   ... and {len(menu_items) - 5} more items")
            else:
                print("❌ No menu items found")
            
            input("\nPress Enter to close browser...")
            
    except Exception as e:
        print(f"💥 Error in debug mode: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import sys
    
    # Check if user wants debug mode
    if len(sys.argv) > 1 and sys.argv[1] == "debug":
        debug_mode()
    else:
        main()