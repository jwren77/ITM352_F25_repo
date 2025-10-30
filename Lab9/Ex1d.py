import csv
import os

csv_filename = "my_custom_spreadsheet.csv"

# Define function
def analyze_salaries(filename):
    if not os.path.exists(filename):
        print(f"File {filename} does not exist.")
        return

    salaries = []

    with open(filename, newline='') as csv_file:
        reader = csv.reader(csv_file)
        headers = next(reader)  # Skip the header row
        print(f"Headers: {headers}")

        salaries_index = headers.index("Annual_Salary")
        for row_data in reader:
            salary = row_data[salaries_index].replace(",", "").replace("$", "").strip()
            if salary:
                salaries.append(float(salary))

    if salaries:
        average_salary = sum(salaries) / len(salaries)
        max_salary = max(salaries)
        min_salary = min(salaries)

        print(f"Average Salary: ${average_salary:,.2f}")
        print(f"Max Salary: ${max_salary:,.2f}")
        print(f"Min Salary: ${min_salary:,.2f}")
    else:
        print("No salary data found.")


# Run it
if not os.path.exists(csv_filename):
    print(f"File {csv_filename} does not exist.")
else:
    print(f"File {csv_filename} found. Analyzing salaries...")
    analyze_salaries(csv_filename)

