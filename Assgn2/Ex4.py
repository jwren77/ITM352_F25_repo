import pandas as pd
import numpy as np
import time
import sys

def display_initial_rows(data):
    """Show the first n rows of sales data"""
    print("\nHow many rows would you like to see?")
    while True:
        try:
            num_rows = int(input("Enter number of rows: "))
            if num_rows > 0:
                print(f"\nFirst {num_rows} rows:")
                print(data.head(num_rows))
                break
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")

def show_employees_by_region(data):
    """Show the number of unique employees in each region"""
    print("\nCreating pivot table: Number of Employees by Region")
    
    # Create pivot table using employee_id and sales_region (or customer_state)
    if 'employee_id' in data.columns and 'sales_region' in data.columns:
        # Use sales_region if available
        pivot_table = pd.pivot_table(
            data,
            values='employee_id',
            index='sales_region', 
            aggfunc='nunique'
        )
        pivot_table.columns = ['Number of Employees']
        print("\nEmployees by Sales Region:")
        print(pivot_table)
    elif 'employee_id' in data.columns and 'customer_state' in data.columns:
        # Use customer_state as region
        pivot_table = pd.pivot_table(
            data,
            values='employee_id',
            index='customer_state',
            aggfunc='nunique' 
        )
        pivot_table.columns = ['Number of Employees']
        print("\nEmployees by Customer State:")
        print(pivot_table)
    else:
        print("Required columns for employee analysis not found.")

def generate_custom_pivot_table(data):
    """Create a custom pivot table based on user selections"""
    print("Custom table")

def exit_program(data):
    """Exit the program"""
    print("Thank you for using the program!")
    print("Goodbye!")
    sys.exit(0)
# Menu options
menu_options = (
    ("Show the first n rows of sales data", display_initial_rows),
    ("Show the number of employees by region", show_employees_by_region),
    ("Exit the program", exit_program)
)

def display_menu():
    """Display the menu and get user selection"""
    print("\n=== Sales Data Analysis Menu ===")
    for i, (title, _) in enumerate(menu_options, start=1):
        print(f"{i}. {title}")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (1-3): "))
            if 1 <= choice <= len(menu_options):
                return choice
            else:
                print(f"Please enter a number between 1 and {len(menu_options)}")
        except ValueError:
            print("Please enter a valid number")

def main():
    """Main function to run the program"""
    # Load the data
    url = 'https://drive.google.com/uc?id=1ujY0WCcePdotG2xdbLyeECFW9lCJ4t-K'
    
    print("Loading CSV file...")
    df = pd.read_csv(url, on_bad_lines="skip")
    print("Data loaded successfully!")
    print("Number of rows:", len(df))
    print("Number of columns:", len(df.columns))
    
    # Clean the data
    df["order_date"] = pd.to_datetime(df["order_date"], format="%m/%d/%Y", errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    df["sales"] = df["quantity"] * df["unit_price"]
    
    # Fill missing values with 0
    df["quantity"] = df["quantity"].fillna(0)
    df["unit_price"] = df["unit_price"].fillna(0)
    df["sales"] = df["sales"].fillna(0)
    
    print("\nWelcome to Sales Data Analysis!")
    print("Data has been loaded and cleaned.")
    
    # Main program loop
    while True:
        user_choice = display_menu()
        
        # Get the function from the menu options
        selected_function = menu_options[user_choice - 1][1]
        
        # Call the selected function with the data
        selected_function(df)

if __name__ == "__main__":
    main()