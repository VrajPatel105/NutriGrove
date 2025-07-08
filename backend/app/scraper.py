from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

class Scraper:
    def __init__(self, date):
        # This automatically handles driver versions:
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.date = date

    def fetch_breakfast(self):
        self.driver.get(f"https://new.dineoncampus.com/umassd/whats-on-the-menu/the-grove/{self.date}/breakfast")
        time.sleep(10)
        all_food_items = []
        counter = 1
        while True:
            try:
                table = self.driver.find_element(By.XPATH, f"/html/body/div/div/div/main/div[1]/div[3]/div/div[2]/div[{counter}]/div[2]/div[2]/table/tbody")
                try:
                    station_name_element = self.driver.find_element(By.XPATH, f"/html/body/div/div/div/main/div[1]/div[3]/div/div[2]/div[{counter}]/div[1]/div[2]/div")
                    station_name = station_name_element.text.strip()
                    print(f"Station Name: {station_name}")
                except Exception as e:
                    station_name = f"Station {counter}"
                    print(f"Could not get station name, using fallback: {station_name}")
                rows = table.find_elements(By.CSS_SELECTOR, 'tr')
                if not rows:
                    break
                print(f"Processing table {counter} ({station_name}) with {len(rows)} rows")
                for row_index, row in enumerate(rows, 1):
                    try:
                        button_click = row.find_element(By.CSS_SELECTOR, 'td:first-child div span')
                        food_name = button_click.text.strip()
                        print(f"Processing: {food_name}")
                        button_click.click()
                        time.sleep(3)
                        wait = WebDriverWait(self.driver, 10)
                        popup = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div/main/div[2]/div")))
                        popup_text = popup.text
                        food_data = {
                            'station_name': station_name,
                            'food_name': food_name,
                            'nutritional_info': popup_text,
                        }
                        all_food_items.append(food_data)
                        print(f"Captured data for: {food_name}")
                        close_button = self.driver.find_element(By.XPATH, "/html/body/div/div/div/main/div[2]/div/button[1]")
                        close_button.click()
                        time.sleep(2)
                    except Exception as e:
                        print(f"Error clicking button in row {row_index}: {e}")
                        continue
                print(f"Finished processing table {counter} ({station_name})")
                counter += 1
            except Exception as e:
                print(f"No more tables found or error with table {counter}: {e}")
                break
        print(f"\nTotal items processed: {len(all_food_items)}")
        with open('backend/app/data/scraped_data/food_items_breakfast.json', 'w', encoding='utf-8') as f:
            json.dump(all_food_items, f, indent=2, ensure_ascii=False)
        print("Data saved to:")
        print("- food_items_breakfast.json (structured data)")
        return True

    def fetch_dinner(self):
        self.driver.get(f"https://new.dineoncampus.com/umassd/whats-on-the-menu/the-grove/{self.date}/dinner")
        time.sleep(10)
        all_food_items = []
        counter = 1
        while True:
            try:
                table = self.driver.find_element(By.XPATH, f"/html/body/div/div/div/main/div[1]/div[3]/div/div[2]/div[{counter}]/div[2]/div[2]/table/tbody")
                try:
                    station_name_element = self.driver.find_element(By.XPATH, f"/html/body/div/div/div/main/div[1]/div[3]/div/div[2]/div[{counter}]/div[1]/div[2]/div")
                    station_name = station_name_element.text.strip()
                    print(f"Station Name: {station_name}")
                except Exception as e:
                    station_name = f"Station {counter}"
                    print(f"Could not get station name, using fallback: {station_name}")
                rows = table.find_elements(By.CSS_SELECTOR, 'tr')
                if not rows:
                    break
                print(f"Processing table {counter} ({station_name}) with {len(rows)} rows")
                for row_index, row in enumerate(rows, 1):
                    try:
                        button_click = row.find_element(By.CSS_SELECTOR, 'td:first-child div span')
                        food_name = button_click.text.strip()
                        print(f"Processing: {food_name}")
                        button_click.click()
                        time.sleep(3)
                        wait = WebDriverWait(self.driver, 10)
                        popup = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div/main/div[2]/div")))
                        popup_text = popup.text
                        food_data = {
                            'station_name': station_name,
                            'food_name': food_name,
                            'nutritional_info': popup_text,
                        }
                        all_food_items.append(food_data)
                        print(f"Captured data for: {food_name}")
                        close_button = self.driver.find_element(By.XPATH, "/html/body/div/div/div/main/div[2]/div/button[1]")
                        close_button.click()
                        time.sleep(2)
                    except Exception as e:
                        print(f"Error clicking button in row {row_index}: {e}")
                        continue
                print(f"Finished processing table {counter} ({station_name})")
                counter += 1
            except Exception as e:
                print(f"No more tables found or error with table {counter}: {e}")
                break
        print(f"\nTotal items processed: {len(all_food_items)}")
        with open('backend/app/data/scraped_data/food_items_dinner.json', 'w', encoding='utf-8') as f:
            json.dump(all_food_items, f, indent=2, ensure_ascii=False)
        print("Data saved to:")
        print("- food_items_dinner.json (structured data)")
        return True

    def fetch_brunch(self):
        self.driver.get(f"https://new.dineoncampus.com/umassd/whats-on-the-menu/the-grove/{self.date}/brunch")
        time.sleep(10)
        all_food_items = []
        counter = 1
        while True:
            try:
                table = self.driver.find_element(By.XPATH, f"/html/body/div/div/div/main/div[1]/div[3]/div/div[2]/div[{counter}]/div[2]/div[2]/table/tbody")
                try:
                    station_name_element = self.driver.find_element(By.XPATH, f"/html/body/div/div/div/main/div[1]/div[3]/div/div[2]/div[{counter}]/div[1]/div[2]/div")
                    station_name = station_name_element.text.strip()
                    print(f"Station Name: {station_name}")
                except Exception as e:
                    station_name = f"Station {counter}"
                    print(f"Could not get station name, using fallback: {station_name}")
                rows = table.find_elements(By.CSS_SELECTOR, 'tr')
                if not rows:
                    break
                print(f"Processing table {counter} ({station_name}) with {len(rows)} rows")
                for row_index, row in enumerate(rows, 1):
                    try:
                        button_click = row.find_element(By.CSS_SELECTOR, 'td:first-child div span')
                        food_name = button_click.text.strip()
                        print(f"Processing: {food_name}")
                        button_click.click()
                        time.sleep(3)
                        wait = WebDriverWait(self.driver, 10)
                        popup = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div/main/div[2]/div")))
                        popup_text = popup.text
                        food_data = {
                            'station_name': station_name,
                            'food_name': food_name,
                            'nutritional_info': popup_text,
                        }
                        all_food_items.append(food_data)
                        print(f"Captured data for: {food_name}")
                        close_button = self.driver.find_element(By.XPATH, "/html/body/div/div/div/main/div[2]/div/button[1]")
                        close_button.click()
                        time.sleep(2)
                    except Exception as e:
                        print(f"Error clicking button in row {row_index}: {e}")
                        continue
                print(f"Finished processing table {counter} ({station_name})")
                counter += 1
            except Exception as e:
                print(f"No more tables found or error with table {counter}: {e}")
                break
        print(f"\nTotal items processed: {len(all_food_items)}")
        with open('backend/app/data/scraped_data/food_items_brunch.json', 'w', encoding='utf-8') as f:
            json.dump(all_food_items, f, indent=2, ensure_ascii=False)
        print("Data saved to:")
        print("- food_items_brunch.json (structured data)")
        return True

    def fetch_lunch(self):
        self.driver.get(f"https://new.dineoncampus.com/umassd/whats-on-the-menu/the-grove/{self.date}/lunch")
        time.sleep(10)
        all_food_items = []
        counter = 1
        while True:
            try:
                table = self.driver.find_element(By.XPATH, f"/html/body/div/div/div/main/div[1]/div[3]/div/div[2]/div[{counter}]/div[2]/div[2]/table/tbody")
                try:
                    station_name_element = self.driver.find_element(By.XPATH, f"/html/body/div/div/div/main/div[1]/div[3]/div/div[2]/div[{counter}]/div[1]/div[2]/div")
                    station_name = station_name_element.text.strip()
                    print(f"Station Name: {station_name}")
                except Exception as e:
                    station_name = f"Station {counter}"
                    print(f"Could not get station name, using fallback: {station_name}")
                rows = table.find_elements(By.CSS_SELECTOR, 'tr')
                if not rows:
                    break
                print(f"Processing table {counter} ({station_name}) with {len(rows)} rows")
                for row_index, row in enumerate(rows, 1):
                    try:
                        button_click = row.find_element(By.CSS_SELECTOR, 'td:first-child div span')
                        food_name = button_click.text.strip()
                        print(f"Processing: {food_name}")
                        button_click.click()
                        time.sleep(3)
                        wait = WebDriverWait(self.driver, 10)
                        popup = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div/main/div[2]/div")))
                        popup_text = popup.text
                        food_data = {
                            'station_name': station_name,
                            'food_name': food_name,
                            'nutritional_info': popup_text,
                        }
                        all_food_items.append(food_data)
                        print(f"Captured data for: {food_name}")
                        close_button = self.driver.find_element(By.XPATH, "/html/body/div/div/div/main/div[2]/div/button[1]")
                        close_button.click()
                        time.sleep(2)
                    except Exception as e:
                        print(f"Error clicking button in row {row_index}: {e}")
                        continue
                print(f"Finished processing table {counter} ({station_name})")
                counter += 1
            except Exception as e:
                print(f"No more tables found or error with table {counter}: {e}")
                break
        print(f"\nTotal items processed: {len(all_food_items)}")
        with open('backend/app/data/scraped_data/food_items_lunch.json', 'w', encoding='utf-8') as f:
            json.dump(all_food_items, f, indent=2, ensure_ascii=False)
        print("Data saved to:")
        print("- food_items_lunch.json (structured data)")
        return True

    def close(self):
        self.driver.quit()