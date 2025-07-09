from scraper import Scraper  # Import your Scraper class
from datetime import datetime
from data.clean_data import clean_data

# Option 1: Use today's date
today_date = datetime.today().strftime('%Y-%m-%d')
scraper = Scraper(today_date)

try:
    
    scraper.fetch_breakfast()
    scraper.fetch_lunch()
    # scraper.fetch_brunch()
    scraper.fetch_dinner()
    print("All data scraped successfully!")
    # cleaning the scraped data
    clean_data.clean_data_func()
    print("All data cleaned")
    
finally:
    scraper.close()