## Running the Scraping Bot

Requires Selenium installed. The Venv setup should include it so running the below commands should execute the bot.

```
python -m venv venv    
source venv/bin/activate
python tingScraper.py
```

## Cleaning the Data

After scraping the data it needs to be processed and converted into map data. Running the below scripts should handle:

```
python geoJSONParser.py    
python parcelParser.py  
python geoJSONParcelParser.py
```