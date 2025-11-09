##ON YOUR OWN: 6.  Use the requests package to retrieve a page of mortgage rate info from the Hawaii Board of Realtors site that lists current local mortgage rates: https://www.hicentral.com/hawaii-mortgage-rates.php 
##Find the rate table and extract each row.

##Output the name of each bank and its current rates per row.

import pandas as pd
import urllib.request
import requests
from bs4 import BeautifulSoup

url = "https://www.hicentral.com/hawaii-mortgage-rates.php"
print("Opening URL...", url)

#Use requests to get the webpage
response = requests.get(url)

try:
    tables = pd.read_html(response.text)
    html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text
    tables = pd.read_html(html)
    rate_table = tables[0]  
    rate_table.columns = [col.strip() for col in rate_table.columns]
    print("\nMortgage Rates from Hawaii Board of Realtors:\n")
    print("\nExtracting rate table rows...\n")
    for index, row in rate_table.iterrows():
        print(f"Row {index}: {list(row.values)}")
except Exception as e:
    print("Error reading the table:", e)
    exit()