from scraper import Scraper
from datetime import datetime
from data.clean_data import FoodDataCleaner

# Use today's date
# today_date = datetime.today().strftime('%Y-%m-%d')
today_date = "2025-07-16"
scraper = Scraper(today_date)

try:
    # # Scrape data directly to database
    scraper.fetch_breakfast()
    scraper.fetch_lunch()
    scraper.fetch_dinner()
    print("All data scraped and saved to database!")
finally:
    scraper.close()    

# Clean the scraped data from database
cleaner = FoodDataCleaner()
cleaned_data = cleaner.clean_food_data()

if cleaned_data:
    print(f"Data cleaned and uploaded! Total items: {len(cleaned_data)}")
else:
    print("Data cleaning failed!")

