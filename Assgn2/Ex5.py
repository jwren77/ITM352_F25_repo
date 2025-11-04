
##Sales Data Analysis Program - Beginner Friendly Version

#This program helps you analyze sales data by creating tables and summaries.
#It can:
##1. Show you rows of data
##2. Count employees by region  
###3. Create custom summary tables
##4. Exit when you're done

#The data includes information about:
#- Sales orders and amounts
#- Employees and their regions
#- Customers and their locations  
####- Products and their categories


import pandas as pd
import numpy as np
import time
import sys

def display_initial_rows(data):
    """Show some rows of the sales data so you can see what it looks like"""
    print("\n=== Looking at the Sales Data ===")
    print("This shows you what the data looks like")
    
    # Ask how many rows to show
    print("\nHow many rows would you like to see? (Try 5 or 10)")
    
    while True:
        try:
            num_rows = int(input("Enter a number: "))
            if num_rows > 0:
                print(f"\nHere are the first {num_rows} rows of data:")
                print(data.head(num_rows))
                print(f"\nEach row represents one sales order")
                break
            else:
                print("Please enter a number greater than 0")
        except ValueError:
            print("Please enter just a number")

def show_employees_by_region(data):
    """Count how many different employees work in each region"""
    print("\n=== Employee Count by Region ===")
    print("This shows how many employees work in each area")
    
    # Count unique employees by state (since that's what we have in the data)
    if 'employee_id' in data.columns and 'customer_state' in data.columns:
        # Create a summary table
        employee_count = pd.pivot_table(
            data,
            values='employee_id',
            index='customer_state',
            aggfunc='nunique',  # Count unique employees
            fill_value=0
        )
        
        # Make the column name clearer
        employee_count.columns = ['Number of Employees']
        
        print("\nEmployees working in each state:")
        print(employee_count)
        print(f"\nTotal states with employees: {len(employee_count)}")
        
    else:
        print("Sorry, can't find employee data in the file")

def show_options_and_get_choice(options, message):
    """Show a list of options and get user's choice"""
    print(f"\n{message}")
    
    # Show all the options with numbers
    for i, option in enumerate(options):
        print(f"{i+1}. {option}")
    
    # Get user input
    user_input = input("Enter your choice (just one number): ").strip()
    
    # Check if input is valid
    try:
        choice_num = int(user_input)
        if 1 <= choice_num <= len(options):
            return options[choice_num - 1]  # Return the selected option
        else:
            print("That number is not in the list. Please try again.")
            return None
    except ValueError:
        print("Please enter just a number.")
        return None

def generate_custom_pivot_table(data):
    """Create a custom pivot table - simplified for beginners"""
    print("\n=== Custom Pivot Table Builder ===")
    print("Let's build a table to analyze your data!")
    
    # Step 1: Choose what to analyze (the numbers)
    print("\n--- Step 1: What do you want to analyze? ---")
    number_columns = ['sales', 'quantity', 'unit_price']  # Keep it simple
    
    what_to_analyze = None
    while what_to_analyze is None:
        what_to_analyze = show_options_and_get_choice(number_columns, "Pick what to analyze:")
    
    # Step 2: Choose how to calculate
    print("\n--- Step 2: How do you want to calculate it? ---")
    calculations = ['sum', 'average', 'count']
    
    how_to_calculate = None
    while how_to_calculate is None:
        how_to_calculate = show_options_and_get_choice(calculations, "Pick how to calculate:")
    
    # Convert 'average' to 'mean' for pandas
    if how_to_calculate == 'average':
        how_to_calculate = 'mean'
    
    # Step 3: Choose how to group the data
    print("\n--- Step 3: How do you want to group the data? ---")
    grouping_options = [
        'customer_state (by state)', 
        'product_category (by product type)',
        'employee_name (by employee)',
        'order_type (by order type)',
        'customer_type (by customer type)'
    ]
    
    group_by = None
    while group_by is None:
        group_by = show_options_and_get_choice(grouping_options, "Pick how to group:")
    
    # Extract just the column name (remove the description)
    group_column = group_by.split(' ')[0]
    
    # Step 4: Ask if they want a second grouping (optional)
    print("\n--- Step 4: Want to add a second grouping? (Optional) ---")
    print("This will create columns in your table")
    
    second_grouping = input("Press Enter to skip, or type 'yes' to add: ").strip().lower()
    
    second_group_column = None
    if second_grouping == 'yes':
        # Show options that aren't already used
        remaining_options = [opt for opt in grouping_options if not opt.startswith(group_column)]
        if remaining_options:
            second_group_by = show_options_and_get_choice(remaining_options, "Pick second grouping:")
            if second_group_by:
                second_group_column = second_group_by.split(' ')[0]
    
    # Step 5: Create the table
    print(f"\n--- Creating Your Table ---")
    print(f"Analyzing: {what_to_analyze}")
    print(f"Calculation: {how_to_calculate}")
    print(f"Grouped by: {group_column}")
    if second_group_column:
        print(f"Also grouped by: {second_group_column}")
    
    try:
        # Create the pivot table
        pivot_table = pd.pivot_table(
            data,
            values=what_to_analyze,
            index=group_column,
            columns=second_group_column if second_group_column else None,
            aggfunc=how_to_calculate,
            fill_value=0
        )
        
        print(f"\n=== Your Custom Table ===")
        
        # Show top 10 rows if the table is large
        if len(pivot_table) > 10:
            print("(Showing top 10 results)")
            print(pivot_table.head(10))
            print(f"\nTotal rows in table: {len(pivot_table)}")
        else:
            print(pivot_table)
            
    except Exception as e:
        print(f"Sorry, couldn't create the table: {str(e)}")
        print("Try different options or ask for help!")

def exit_program(data):
    """Exit the program"""
    print("Thank you for using the program!")
    print("Goodbye!")
    sys.exit(0)
# Menu options
menu_options = (
    ("Show the first n rows of sales data", display_initial_rows),
    ("Show the number of employees by region", show_employees_by_region),
    ("Create custom pivot table", generate_custom_pivot_table),
    ("Exit the program", exit_program)
)

def display_menu():
    """Display the menu and get user selection"""
    print("\n=== Sales Data Analysis Menu ===")
    for i, (title, _) in enumerate(menu_options, start=1):
        print(f"{i}. {title}")
    
    while True:
        try:
            choice = int(input(f"\nEnter your choice (1-{len(menu_options)}): "))
            if 1 <= choice <= len(menu_options):
                return choice
            else:
                print(f"Please enter a number between 1 and {len(menu_options)}")
        except ValueError:
            print("Please enter a valid number")

def main():
    """This is the main function that runs everything"""
    print("=== Sales Data Analysis Program ===")
    print("Loading sales data from the internet...")
    
    # Get the data from Google Drive
    url = 'https://drive.google.com/uc?id=1ujY0WCcePdotG2xdbLyeECFW9lCJ4t-K'
    
    try:
        # Load the data into a table (called a DataFrame)
        df = pd.read_csv(url, on_bad_lines="skip")
        print("✓ Data loaded successfully!")
        print(f"✓ Found {len(df)} sales orders")
        print(f"✓ Data has {len(df.columns)} different pieces of information")
        
        # Clean up the data to make sure numbers are actually numbers
        print("\nCleaning up the data...")
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
        df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
        df["sales"] = df["quantity"] * df["unit_price"]  # Calculate total sales
        
        # Replace any missing values with 0
        df["quantity"] = df["quantity"].fillna(0)
        df["unit_price"] = df["unit_price"].fillna(0)
        df["sales"] = df["sales"].fillna(0)
        
        print("✓ Data is ready to analyze!")
        
        # Show the menu and let user choose what to do
        print("\n" + "="*50)
        print("Ready! Choose what you want to do:")
        
        # Keep showing the menu until user chooses to exit
        while True:
            user_choice = display_menu()
            
            # Run the function the user chose
            selected_function = menu_options[user_choice - 1][1]
            selected_function(df)
            
    except Exception as e:
        print(f"Sorry, something went wrong: {e}")
        print("Check your internet connection and try again")

if __name__ == "__main__":
    main()