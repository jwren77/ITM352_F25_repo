#Read in csv file of homes data and 
#and turn it into a Pandas dataframe. 
#Print out the dimensions of the data frame and show the first 10 rows

#Select only properties that have 500 or more units. Drop some unnecessary columns and print the first 10 rows

#Look at the data types. Determine which data types are incorrect and coerce them to the correct data type. Look at the data types now and print the cleaned data.

#We have some null values and duplicates.  Drop those rows and print out the results. 

#Filter out 0 sales and print the results. Compute and display the average sales price 

#What is the purpose of using a CSV file rather than JSON or another data format?

import pandas as pd

df_homes = pd.read_csv('homes_data.csv')

# Normalize column names to avoid KeyError from unexpected capitalization/spacing
# e.g. header has 'sale_price' not 'sales_price' and may contain spaces
df_homes.columns = df_homes.columns.str.strip().str.lower().str.replace(' ', '_')

#print dimensions and first 10 rows
shape = df_homes.shape
print(f"The homes data frame has {shape[0]} rows and {shape[1]} columns.")
print("First 10 rows of the homes data frame:")


df_big_homes = df_homes[df_homes.units >= 500]

#select only homes with 500 or more units



#Drop unnecessary columns
df_big_homes = df_big_homes.drop(columns=["id", "easement"])

print(df_big_homes.head(10))

#look at data types
print(df_big_homes.dtypes)

#drop rows with null values
df_big_homes = df_big_homes.dropna()

#drop duplicate 
df_big_homes = df_big_homes.drop_duplicates()

#convert columns to appropriate data types
df_big_homes["sale_price"] = pd.to_numeric(df_big_homes["sale_price"], errors='coerce')
df_big_homes["land_sqft"] = pd.to_numeric(df_big_homes["land_sqft"], errors='coerce')
df_big_homes["gross_sqft"] = pd.to_numeric(df_big_homes["gross_sqft"], errors='coerce')


#print out first 10 rows of the cleaned datafram

print("After dropping nulls and duplicates:")
print(df_big_homes.head(10))

df_big_homes = df_big_homes[df_big_homes["sale_price"] > 0]
print("After dropping 0 sales price\n", df_big_homes.head(10))

#calculate average sales price
average_sales_price = df_big_homes["sale_price"].mean()
print(f"Average sale price for properties with >0 sales: {average_sales_price}")
