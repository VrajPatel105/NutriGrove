from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

s = Service(r"C:\My Projects\Advanced Web Scraping\msedgedriver.exe")
driver = webdriver.Edge(service=s)
driver.get("https://new.dineoncampus.com/umassd/whats-on-the-menu/the-grove/2025-06-26/lunch")
# wait for some time to load the website
time.sleep(10)

# List to store all food item data
all_food_items = []

counter = 1

while True:
    try:
        # Try to find the current table
        table = driver.find_element(By.XPATH, f"/html/body/div/div/div/main/div[1]/div[3]/div/div[2]/div[{counter}]/div[2]/div[2]/table/tbody")
        
        # Get the station name for this table
        try:
            station_name_element = driver.find_element(By.XPATH, f"/html/body/div/div/div/main/div[1]/div[3]/div/div[2]/div[{counter}]/div[1]/div[2]/div")
            station_name = station_name_element.text.strip()
            print(f"Station Name: {station_name}")
        except Exception as e:
            station_name = f"Station {counter}"  # Fallback name
            print(f"Could not get station name, using fallback: {station_name}")
        
        # Get all rows in the current table
        rows = table.find_elements(By.CSS_SELECTOR, 'tr')
        
        if not rows:  # If no rows found, break
            break
            
        print(f"Processing table {counter} ({station_name}) with {len(rows)} rows")
        
        # Process each row in the current table
        for row_index, row in enumerate(rows, 1):
            try:
                button_click = row.find_element(By.CSS_SELECTOR, 'td:first-child div span')
                
                # Get the food item name before clicking (for reference)
                food_name = button_click.text.strip()
                print(f"Processing: {food_name}")
                
                button_click.click()
                time.sleep(3)
                
                # Wait for the popup to appear
                wait = WebDriverWait(driver, 10)
                popup = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div/main/div[2]/div")))
                
                # Get all text from the popup
                popup_text = popup.text
                
                # Store the data
                food_data = {
                    'station_name': station_name,
                    'food_name': food_name,
                    'nutritional_info': popup_text,
                }
                
                all_food_items.append(food_data)
                print(f"Captured data for: {food_name}")
                
                # Close the popup
                close_button = driver.find_element(By.XPATH, "/html/body/div/div/div/main/div[2]/div/button[1]")
                close_button.click()
                time.sleep(2)
                
            except Exception as e:
                print(f"Error clicking button in row {row_index}: {e}")
                continue
        
        print(f"Finished processing table {counter} ({station_name})")
        counter += 1
        
    except Exception as e:
        print(f"No more tables found or error with table {counter}: {e}")
        break  # Exit when no more tables are found

# Save all data to files
print(f"\nTotal items processed: {len(all_food_items)}")

# Save as JSON
with open('food_items_data.json', 'w', encoding='utf-8') as f:
    json.dump(all_food_items, f, indent=2, ensure_ascii=False)

print("Data saved to:")
print("- food_items_data.json (structured data)")
driver.quit()

# type: ignore