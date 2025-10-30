#Adding to the program you created in 1. Create a pivot table out of this data, aggregating sales by region, with columns defined by order_type (which is either Retail or Wholesale) and totals column (i.e. “margins”). You must create a new sales column in the dataframe from the quantity and unit_price columns (sales = quantity * price) before creating the pivot table.  Use Pandas to_numeric to coerce quantity and unit_price to numeric before computing sales. Explain why you should do this. Use the numpy sum function rather than the built-in sum function. Set the Panda option "display.max_columns", None, to force the display of all columns. Explain what this does and if you need to do this before or after you create the pivot table.

import pandas as pd
import numpy as np
url = 'https://drive.google.com/uc?id=1ujY0WCcePdotG2xdbLyeECFW9lCJ4t-K'
pd.set_option("display.max_columns", None)

try:
    df = pd.read_csv(url, engine="pyarrow", on_bad_lines="skip")
    df["order_date"] = pd.to_datetime(df["order_date"], errors='coerce')
    df["sales"] = df["quantity"] * df["unit_price"]
    #create the pivot table aggregating sales by region and order_type
    pivot_table = pd.pivot_table(df,
                                 values="sales",
                                 index="sales_region",
                                 columns="order_type",
                                 aggfunc=np.sum,
                                 margins=True, #add a total column
                                 margins_name="Total") #name of the total column
    print(pivot_table)
                                 
   
except Exception as e:
    print("Error reading the CSV file:", e)