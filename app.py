from scraper import Scraper  # Import your Scraper class
from datetime import datetime

# Option 1: Use today's date
today_date = datetime.today().strftime('%Y-%m-%d')
scraper = Scraper(today_date)

try:
    # Run all meal types
    scraper.fetch_breakfast()
    scraper.fetch_lunch()
    # scraper.fetch_brunch()
    scraper.fetch_dinner()
    print("All data scraped successfully!")
finally:
    scraper.close()