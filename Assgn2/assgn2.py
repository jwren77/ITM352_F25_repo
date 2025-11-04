import pandas as pd
import numpy as np
import pyarrow as pa
import time

url = 'https://drive.google.com/uc?id=1ujY0WCcePdotG2xdbLyeECFW9lCJ4t-K'

def load_csv(file_path):
    print(f"Loading CSV file from {file_path}...")
    start_time = time.time()
    df = pd.read_csv(file_path, engine="pyarrow", on_bad_lines="skip")
    end_time = time.time()
    print(f"CSV file loaded successfully in {end_time - start_time:.2f} seconds.")
    pd.set_option("display.max_columns", None)
    pd.set_option("display.float_format", "${:,.2f}".format)
    return df

try:
    print(f"Reading CSV file from {url}...")
    start_time = time.time()
    df = pd.read_csv(url, engine="pyarrow", on_bad_lines="skip")
    end_time = time.time()
    print(f"CSV file read successfully in {end_time - start_time:.2f} seconds.")
    print("Number of rows read:", len(df))
    print("Number of columns read:", len(df.columns))

    # make sure required columns exist before using them
    required_columns = ["quantity", "unit_price", "order_date",
                        "customer_state", "customer_type", "order_type"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    # clean types (safe)
    df["order_date"] = pd.to_datetime(df["order_date"], format="%m/%d/%Y", errors="coerce")
    df["quantity"]   = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")

    # calc sales
    df["sales"] = df["quantity"] * df["unit_price"]

    # fill numeric NaNs
    df[["quantity", "unit_price", "sales"]] = df[["quantity", "unit_price", "sales"]].fillna(0)

    # pivot (mean sales by state x (customer_type, order_type))
    pivot_table = pd.pivot_table(
        df,
        values="sales",
        index="customer_state",
        columns=["customer_type", "order_type"],
        aggfunc=np.mean,
        margins=True,
        margins_name="Total"
    )

    print(pivot_table)

except FileNotFoundError as e:
    print("File was not found", e)
except pd.errors.EmptyDataError as e:
    print("File is empty", e)
except pd.errors.ParserError as e:
    print("Error parsing data", e)
except Exception as e:
    print("Unexpected error", e)