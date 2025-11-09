# sales_dashboard.py

import sys
import time
import pandas as pd
import numpy as np

DEFAULT_URL = "https://drive.google.com/uc?id=1Fv_vhoN4sTrUaozFPfzr0NCyHJLIeXEA"  # assignment URL
FALLBACK_URL = "https://drive.google.com/uc?id=1ujY0WCcePdotG2xdbLyeECFW9lCJ4t-K" # your earlier URL
TEST_OUTFILE = "sales_data_test.csv"

# ---- Settings (you can flip these) -----------------------------------------
FILL_PIVOT_WITH_MEANS = True   # if True: fill NaNs with column means; else with zeros
USE_PYARROW_ENGINE    = True   # if pyarrow not installed, code will fall back automatically
# ---------------------------------------------------------------------------

# Store analytics results by name -> DataFrame
analytics_store = {}

# ----------------- Utility & Input Helpers ---------------------------------
def safe_read_csv(path_or_url: str) -> pd.DataFrame:
    """Load CSV with timing and engine fallback."""
    print(f"\nLoading CSV from: {path_or_url}")
    start = time.time()
    engine = "pyarrow" if USE_PYARROW_ENGINE else None
    try:
        df = pd.read_csv(path_or_url, on_bad_lines="skip", engine=engine) if engine else pd.read_csv(path_or_url, on_bad_lines="skip")
    except Exception:
        # fallback if pyarrow not available or any engine error
        df = pd.read_csv(path_or_url, on_bad_lines="skip")
    secs = time.time() - start
    print(f"✓ Loaded in {secs:.2f} sec")
    return df

def list_columns(df: pd.DataFrame):
    print("\nAvailable columns:")
    for c in df.columns:
        print(f"  - {c}")

def export_prompt(df: pd.DataFrame, default_name: str):
    """Ask user to export a DataFrame to Excel."""
    if df is None or not isinstance(df, pd.DataFrame):
        return
    ans = input("\nExport this result to Excel? (y/N): ").strip().lower()
    if ans == "y":
        name = input(f"Enter filename (default: {default_name}.xlsx): ").strip() or f"{default_name}.xlsx"
        try:
            df.to_excel(name, index=True)
            print(f"✓ Saved: {name}")
        except Exception as e:
            print(f"Could not save file: {e}")

def ask_yes_no(prompt: str) -> bool:
    return input(f"{prompt} (y/N): ").strip().lower() == "y"

def ask_date_range(df: pd.DataFrame) -> pd.DataFrame:
    """Filter by date range if order_date exists. Returns possibly filtered df."""
    if "order_date" not in df.columns:
        return df
    ask = input("\nFilter by date range? Press Enter to skip, or type 'yes': ").strip().lower()
    if ask != "yes":
        return df
    # ensure datetime
    d = df.copy()
    d["order_date"] = pd.to_datetime(d["order_date"], errors="coerce")
    start = input("Start date (YYYY-MM-DD), Enter to skip: ").strip()
    end   = input("End   date (YYYY-MM-DD), Enter to skip: ").strip()
    if start:
        d = d[d["order_date"] >= pd.to_datetime(start, errors="coerce")]
    if end:
        d = d[d["order_date"] <= pd.to_datetime(end, errors="coerce")]
    return d

def ask_row_range(df: pd.DataFrame) -> pd.DataFrame:
    """Filter by row range or list before analysis."""
    ans = input("\nUse a subset of rows? Enter 'start:end', '1,5,8', or press Enter to skip: ").strip()
    if not ans:
        return df
    try:
        if ":" in ans:
            s, e = ans.split(":")
            s = int(s) if s else 0
            e = int(e) if e else len(df)
            return df.iloc[s:e]
        else:
            idxs = [int(x) for x in ans.split(",") if x.strip().isdigit()]
            return df.iloc[idxs]
    except Exception:
        print("Invalid row selection. Using all rows.")
        return df

def with_subset(df: pd.DataFrame) -> pd.DataFrame:
    """Apply date-range and row-range filters before running an analytic."""
    d = ask_date_range(df)
    d = ask_row_range(d)
    return d

def fill_pivot(df: pd.DataFrame) -> pd.DataFrame:
    """Replace NaNs in pivot table per assignment option."""
    if df is None or not isinstance(df, pd.DataFrame):
        return df
    if FILL_PIVOT_WITH_MEANS:
        means = df.mean(numeric_only=True)
        return df.fillna(means)
    else:
        return df.fillna(0)

def add_to_store(name: str, table: pd.DataFrame):
    if isinstance(table, pd.DataFrame):
        analytics_store[name] = table.copy()

def choose_from_list(options, prompt):
    print(f"\n{prompt}")
    for i, op in enumerate(options, 1):
        print(f"{i}. {op}")
    inp = input("Enter number: ").strip()
    try:
        k = int(inp)
        if 1 <= k <= len(options):
            return options[k-1]
    except:
        pass
    print("Invalid selection.")
    return None

# ----------------- Data Loading & Preparation (R1) --------------------------
def load_sales_data() -> pd.DataFrame:
    """R1: load data, show timing, rows, columns; fill missing; verify; write 10-row test file; summary."""
    print("\n=== Load Sales Data ===")
    # let user choose default URL, fallback, or custom
    print("Data source options:")
    print("  1. Assignment URL (recommended)")
    print("  2. Alternate URL (your earlier link)")
    print("  3. Enter my own path/URL")
    choice = input("Choose (1/2/3): ").strip()
    if choice == "2":
        src = FALLBACK_URL
    elif choice == "3":
        src = input("Enter a local path or URL: ").strip()
    else:
        src = DEFAULT_URL

    try:
        df = safe_read_csv(src)
    except Exception as e:
        print(f"ERROR: could not load data: {e}")
        sys.exit(1)

    # Show size and columns
    print(f"Rows: {len(df):,} | Columns: {len(df.columns):,}")
    list_columns(df)

    # Defensive: types and derived fields
    # order_date
    if "order_date" in df.columns:
        df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    # quantity, unit_price
    for col in ["quantity", "unit_price"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    # sales
    if "sales" not in df.columns and all(c in df.columns for c in ["quantity", "unit_price"]):
        df["sales"] = df["quantity"] * df["unit_price"]

    # Replace missing base data with zeros for numeric columns
    num_cols = df.select_dtypes(include=["number"]).columns
    df[num_cols] = df[num_cols].fillna(0)

    # Required field check for built-in analytics
    required_map = {
        "1_Show first n rows": [],  # no required
        "2_Total sales by region and order_type": ["sales", "order_type"],
        "3_Average sales by region with average by state and sale type": ["sales", "order_type", "customer_state"],
        "4_Sales by customer type and order type by state": ["sales", "customer_type", "order_type", "customer_state"],
        "5_Total qty & price by region and product": ["quantity", "sales", ("sales_region", "customer_state"), "product_category"],
        "6_Total qty & price by customer type": ["quantity", "sales", "customer_type", "order_type"],
        "7_Max & min sale price by category": [("unit_price", "sale_price", "unitprice", "price"), "product_category"],
        "8_Unique employees by region": ["employee_id", ("sales_region","customer_state")],
        "9_Custom pivot": [],  # validated inside
        "10_Exit": []
    }

    # Normalize region and price naming (prefer dd if exists)
    # We'll dynamically resolve region col and price col in analytics
    print("\n=== Summary (post-load) ===")
    total_orders = len(df)
    n_employees  = df["employee_id"].nunique() if "employee_id" in df.columns else 0
    regions      = df["sales_region"].nunique() if "sales_region" in df.columns else (df["customer_state"].nunique() if "customer_state" in df.columns else 0)
    date_min     = df["order_date"].min() if "order_date" in df.columns else None
    date_max     = df["order_date"].max() if "order_date" in df.columns else None
    n_customers  = df["customer_id"].nunique() if "customer_id" in df.columns else 0
    n_products   = df["product_category"].nunique() if "product_category" in df.columns else 0
    n_states     = df["customer_state"].nunique() if "customer_state" in df.columns else 0
    total_sales  = float(df["sales"].sum()) if "sales" in df.columns else 0.0
    total_qty    = float(df["quantity"].sum()) if "quantity" in df.columns else 0.0

    print(f"Total orders: {total_orders:,}")
    print(f"Unique employees: {n_employees}")
    print(f"Sales regions/states: {regions}")
    if date_min is not None and pd.notna(date_min):
        print(f"Date range: {str(date_min)[:10]} to {str(date_max)[:10]}")
    print(f"Unique customers: {n_customers}")
    print(f"Product categories: {n_products}")
    print(f"Unique states: {n_states}")
    print(f"Total sales amount: ${total_sales:,.2f}")
    print(f"Total quantity sold: {total_qty:,.2f}")

    # Write test file with first 10 rows (for faster dev)
    try:
        df.head(10).to_csv(TEST_OUTFILE, index=False)
        print(f"\n✓ Wrote {TEST_OUTFILE} (first 10 rows)")
    except Exception as e:
        print(f"Could not write test file: {e}")

    return df, required_map

def resolve_region_column(df: pd.DataFrame) -> str:
    if "sales_region" in df.columns:
        return "sales_region"
    if "customer_state" in df.columns:
        return "customer_state"
    return None

def resolve_unit_price_column(df: pd.DataFrame) -> str:
    # Handle various possible names
    for c in ["unit_price", "sale_price", "unitprice", "price"]:
        if c in df.columns:
            return c
    return None

# ----------------- Menu & Analytics (R2, R3) -------------------------------
def display_initial_rows(df: pd.DataFrame):
    print("\n=== Show First n Rows ===")
    total = len(df)
    print(f"There are {total} rows.")
    print("Enter a number 1 to {total}, or 'all', or press Enter to skip.")
    choice = input("Your choice: ").strip().lower()
    if choice == "":
        print("Skipped.")
        return None
    if choice == "all":
        out = df.copy()
    else:
        if not choice.isdigit():
            print("Invalid input.")
            return None
        n = int(choice)
        if not (1 <= n <= total):
            print("Out of range.")
            return None
        out = df.head(n)
    print(out)
    add_to_store("First_n_rows", out)
    export_prompt(out, "first_n_rows")
    return out

def total_sales_by_region_and_order_type(df: pd.DataFrame):
    print("\n=== Total Sales by Region and order_type ===")
    d = with_subset(df)
    region = resolve_region_column(d)
    if region is None or "order_type" not in d.columns or "sales" not in d.columns:
        print("Missing required columns.")
        return None
    piv = pd.pivot_table(d, values="sales", index=region, columns="order_type", aggfunc="sum")
    piv = fill_pivot(piv)
    print(piv)
    add_to_store("Sales_by_region_order_type", piv)
    export_prompt(piv, "sales_by_region_order_type")
    return piv

def average_sales_by_region_with_state_sale_type(df: pd.DataFrame):
    print("\n=== Average Sales by Region with avg by State & Sale Type ===")
    d = with_subset(df)
    region = resolve_region_column(d)
    if region is None or "order_type" not in d.columns or "customer_state" not in d.columns or "sales" not in d.columns:
        print("Missing required columns.")
        return None
    piv = pd.pivot_table(
        d, values="sales", index=region, columns=["customer_state", "order_type"], aggfunc="mean"
    )
    piv = fill_pivot(piv)
    print(piv)
    add_to_store("Avg_sales_region_state_type", piv)
    export_prompt(piv, "avg_sales_region_state_type")
    return piv

def sales_by_customer_type_and_order_type_by_state(df: pd.DataFrame):
    print("\n=== Sales by Customer Type & Order Type by State ===")
    d = with_subset(df)
    if any(c not in d.columns for c in ["customer_state", "customer_type", "order_type", "sales"]):
        print("Missing required columns.")
        return None
    piv = pd.pivot_table(
        d, values="sales", index=["customer_state", "customer_type"], columns="order_type", aggfunc="sum"
    )
    piv = fill_pivot(piv)
    print(piv)
    add_to_store("Sales_by_custtype_ordertype_state", piv)
    export_prompt(piv, "sales_by_custtype_ordertype_state")
    return piv

def total_qty_price_by_region_and_product(df: pd.DataFrame):
    print("\n=== Total Quantity & Sales by Region and Product ===")
    d = with_subset(df)
    region = resolve_region_column(d)
    if region is None or any(c not in d.columns for c in ["product_category", "quantity", "sales"]):
        print("Missing required columns.")
        return None
    piv = pd.pivot_table(
        d, values=["quantity", "sales"], index=[region, "product_category"], aggfunc="sum"
    )
    piv = fill_pivot(piv)
    print(piv)
    add_to_store("Qty_sales_by_region_product", piv)
    export_prompt(piv, "qty_sales_by_region_product")
    return piv

def total_qty_price_by_customer_type(df: pd.DataFrame):
    print("\n=== Total Quantity & Sales by Customer Type (by Order Type) ===")
    d = with_subset(df)
    if any(c not in d.columns for c in ["customer_type", "order_type", "quantity", "sales"]):
        print("Missing required columns.")
        return None
    piv = pd.pivot_table(
        d, values=["quantity", "sales"], index="customer_type", columns="order_type", aggfunc="sum"
    )
    piv = fill_pivot(piv)
    print(piv)
    add_to_store("Qty_sales_by_customer_type", piv)
    export_prompt(piv, "qty_sales_by_customer_type")
    return piv

def max_min_sale_price_by_category(df: pd.DataFrame):
    print("\n=== Max & Min Sale Price by Category ===")
    d = with_subset(df)
    price_col = resolve_unit_price_column(d)
    if price_col is None or "product_category" not in d.columns:
        print("Missing required columns.")
        return None
    piv = pd.pivot_table(
        d, values=price_col, index="product_category", aggfunc=["max", "min"]
    )
    piv = fill_pivot(piv)
    print(piv)
    add_to_store("Max_min_price_by_category", piv)
    export_prompt(piv, "max_min_price_by_category")
    return piv

def unique_employees_by_region(df: pd.DataFrame):
    print("\n=== Number of Unique Employees by Region ===")
    d = with_subset(df)
    region = resolve_region_column(d)
    if region is None or "employee_id" not in d.columns:
        print("Missing required columns.")
        return None
    piv = pd.pivot_table(d, values="employee_id", index=region, aggfunc=pd.Series.nunique)
    piv.columns = ["unique_employees"] if isinstance(piv, pd.DataFrame) else ["unique_employees"]
    piv = fill_pivot(piv if isinstance(piv, pd.DataFrame) else pd.DataFrame(piv))
    print(piv)
    add_to_store("Unique_employees_by_region", piv)
    export_prompt(piv, "unique_employees_by_region")
    return piv

# ----------------- R4: Custom Pivot Table Generator -------------------------
def get_multi_choice(options, prompt):
    """Return list of selected items from options."""
    print(f"\n{prompt}")
    for i, op in enumerate(options, 1):
        print(f"{i}. {op}")
    raw = input("Enter numbers separated by commas (Enter to skip): ").strip()
    if not raw:
        return []
    out = []
    try:
        for x in raw.split(","):
            k = int(x.strip())
            if 1 <= k <= len(options):
                out.append(options[k-1])
    except:
        print("Invalid entries ignored.")
    return out

def custom_pivot(df: pd.DataFrame):
    print("\n=== Custom Pivot Table Generator ===")
    d = with_subset(df)

    row_options = list(d.columns)
    rows = get_multi_choice(row_options, "Select rows (group by):")
    if not rows:
        print("At least one row is required.")
        return None

    # columns (cannot repeat rows)
    col_options = [c for c in d.columns if c not in rows]
    cols = get_multi_choice(col_options, "Select columns (optional):")

    # numeric values
    val_options = list(d.select_dtypes(include=["number"]).columns)
    if not val_options:
        print("No numeric columns available for values.")
        return None
    values = get_multi_choice(val_options, "Select value columns (numeric):")
    if not values:
        print("At least one value column is required.")
        return None

    agg_options = ["sum", "mean", "count"]
    agg_choice = choose_from_list(agg_options, "Select aggregation:")
    if not agg_choice:
        return None

    piv = pd.pivot_table(
        d,
        index=rows,
        columns=cols if cols else None,
        values=values if len(values) > 1 else values[0],
        aggfunc=agg_choice
    )
    piv = fill_pivot(piv)
    print(piv)
    add_to_store("Custom_pivot", piv)
    export_prompt(piv, "custom_pivot")
    return piv

# ----------------- Extra Analytic (percentage by region & product) ----------
def percent_qty_sales_by_region_product(df: pd.DataFrame):
    print("\n=== % of Quantity & Sales by Region and Product ===")
    d = with_subset(df)
    region = resolve_region_column(d)
    if region is None or any(c not in d.columns for c in ["product_category", "quantity", "sales"]):
        print("Missing required columns.")
        return None
    piv = pd.pivot_table(
        d, values=["quantity", "sales"], index=[region, "product_category"], aggfunc="sum"
    )
    # Compute percentage of totals (per region, per metric)
    piv = piv.sort_index()
    # groupby region level then compute percent within region for each metric
    for metric in ["quantity", "sales"]:
        if metric in piv.columns:
            total_by_region = piv[metric].groupby(level=0).transform("sum")
            piv[f"{metric}_pct_in_region"] = np.where(total_by_region != 0, (piv[metric] / total_by_region) * 100.0, 0.0)
    piv = fill_pivot(piv)
    print(piv)
    add_to_store("Pct_qty_sales_by_region_product", piv)
    export_prompt(piv, "pct_qty_sales_by_region_product")
    return piv

# ----------------- History / Compare ---------------------------------------
def show_saved_results():
    print("\n=== Saved Analytics ===")
    if not analytics_store:
        print("No stored results yet.")
        return
    for i, k in enumerate(analytics_store.keys(), 1):
        print(f"{i}. {k}")

def compare_two_results():
    print("\n=== Compare Two Stored Results ===")
    if len(analytics_store) < 2:
        print("Need at least two stored results.")
        return
    keys = list(analytics_store.keys())
    for i, k in enumerate(keys, 1):
        print(f"{i}. {k}")
    try:
        a = int(input("Pick first (number): ").strip())
        b = int(input("Pick second (number): ").strip())
        k1, k2 = keys[a-1], keys[b-1]
        print(f"\n--- {k1} ---")
        print(analytics_store[k1])
        print(f"\n--- {k2} ---")
        print(analytics_store[k2])
    except Exception:
        print("Invalid selection.")

# ----------------- Menu Construction (R2) -----------------------------------
def build_menu(df: pd.DataFrame, required_map: dict):
    """Build menu; remove items whose required columns are missing."""
    # Label -> function mapping in the R2 order (1..10)
    region = resolve_region_column(df)
    price_col = resolve_unit_price_column(df)

    menu_defs = [
        ("Show the first n rows of sales data",                display_initial_rows,                          "1_Show first n rows"),
        ("Total sales by region and order_type",               total_sales_by_region_and_order_type,          "2_Total sales by region and order_type"),
        ("Average sales by region with average sales by state and sale type",
                                                              average_sales_by_region_with_state_sale_type,  "3_Average sales by region with average by state and sale type"),
        ("Sales by customer type and order type by state",     sales_by_customer_type_and_order_type_by_state,"4_Sales by customer type and order type by state"),
        ("Total sales quantity and price by region and product", total_qty_price_by_region_and_product,       "5_Total qty & price by region and product"),
        ("Total sales quantity and price customer type",       total_qty_price_by_customer_type,              "6_Total qty & price by customer type"),
        ("Max and min sales price of sales by category",       max_min_sale_price_by_category,                "7_Max & min sale price by category"),
        ("Number of unique employees by region",               unique_employees_by_region,                    "8_Unique employees by region"),
        ("Create a custom pivot table",                        custom_pivot,                                  "9_Custom pivot"),
        ("Exit",                                               lambda df: sys.exit(0),                        "10_Exit"),
    ]

    def has_requirements(df, req):
        # req items can be strings or tuples (alternate names). Empty -> ok
        for item in req:
            if isinstance(item, tuple):
                # any of these names satisfies it
                if not any(name in df.columns for name in item):
                    return False
            else:
                if item and item not in df.columns:
                    return False
        return True

    filtered = []
    for label, fn, key in menu_defs:
        req = required_map.get(key, [])
        if has_requirements(df, req):
            filtered.append((label, fn))
        else:
            print(f"(Info) Removed menu item (missing fields): {label}")
    # Extra items (beyond R2 core menu)
    filtered += [
        ("[Extra] Show saved results",           lambda d: show_saved_results()),
        ("[Extra] Compare two saved results",    lambda d: compare_two_results()),
        ("[Extra] % of qty & sales by region/product", percent_qty_sales_by_region_product),
    ]
    return tuple(filtered)

def show_menu(menu):
    print("\n--- Sales Data Dashboard ---")
    for i, (label, _) in enumerate(menu, 1):
        print(f"{i}. {label}")
    while True:
        try:
            choice = int(input(f"\nEnter your choice (1-{len(menu)}): ").strip())
            if 1 <= choice <= len(menu):
                return choice
            print("Out of range.")
        except ValueError:
            print("Please enter a number.")

# ----------------- Main -----------------------------------------------------
def main():
    df, required_map = load_sales_data()
    menu = build_menu(df, required_map)

    while True:
        sel = show_menu(menu)
        _, fn = menu[sel-1]
        try:
            fn(df)
        except SystemExit:
            raise
        except Exception as e:
            print(f"An error occurred in that analytic: {e}")

if __name__ == "__main__":
    main()