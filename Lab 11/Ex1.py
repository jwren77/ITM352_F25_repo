#Read the CSV file from the URL using exception handling and convert the data types using the pyarrow data type backend. Have it skip bad lines read in. Explain why you want to do these things (exception handling, pyarrow conversion, skip bad lines). Explain why it’s better to convert the data while it is read rather than after. If you received warnings, how do you address these?

#Use Pandas to convert the order_date column into a standard date representation. Why do you want to do this? If you received warnings, how do you address these?
#This is the URL you can use to directly access the file using pd.read_csv()

#https://drive.google.com/uc?id=1ujY0WCcePdotG2xdbLyeECFW9lCJ4t-K

import pandas as pd
url = 'https://drive.google.com/uc?id=1ujY0WCcePdotG2xdbLyeECFW9lCJ4t-K'

pd.set_option("display.max_columns", None)

try:
    df = pd.read_csv(url, engine="pyarrow", on_bad_lines="skip")
    df["order_date"] = pd.to_datetime(df["order_date"], errors='coerce')
    print(df.head())
    print(df.info())
except Exception as e:
    print("Error reading the CSV file:", e)
    
    

