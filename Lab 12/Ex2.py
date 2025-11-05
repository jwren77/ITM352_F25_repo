#Open a url from the US treasury and extract its information as a dataframe print the one month treasury rates

import pandas as pd
import urllib.request
import ssl



ssl._create_default_https_context = ssl._create_unverified_context

url="https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value_month=202410"

#Open the web page and save it as a dataframe
print("Opening URL...", url)
try:
    table = pd.read_html(url)
    interest_rate_table = table[0]
    #print(interest_rate_table.columns)
    #print(interest_rate_table.head())

    #print the table of one month interest rates
    print("One Month Treasury Rates:\n")
    for index, row in interest_rate_table.iterrows():
        print(f"Index: {index}, Date: {row['Date']}, 1 Month Rate: {row['1 Mo']}")
        

except Exception as e:
    print("error reading the table:", e)
    exit()