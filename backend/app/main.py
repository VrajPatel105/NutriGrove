from scraper import Scraper  # Import your Scraper class
from datetime import datetime
from data.clean_data import FoodDataCleaner
from database import SupabaseUploader

# Option 1: Use today's date
today_date = datetime.today().strftime('%Y-%m-%d')
scraper = Scraper(today_date)

try:
    
    # scraper.fetch_breakfast()
    # scraper.fetch_lunch()
    # # scraper.fetch_brunch()
    # scraper.fetch_dinner()
    # print("All data scraped successfully!")
    # # cleaning the scraped data
    # FoodDataCleaner.clean_food_data()
    # print("All data cleaned")

    # Create uploader instance and upload
    uploader = SupabaseUploader()
    uploader.upload_json_file('backend/app/data/cleaned_data/all_food_items_cleaned.json')
    print('Data uploaded to database')

    
finally:
    scraper.close()