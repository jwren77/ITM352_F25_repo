#ask the user to insert a floating point number between 1 and 100
#Square the number and return the value to the user rounded to 2 decimal places
#Name Joe Wren
# Date 9/5/2025

value_entered = input("Please enter a floating point number between 1-100: ")
value_entered_float = float(value_entered)
squared_value = value_entered_float ** 2
rounded_value = round(squared_value, 2)

print(f"The square of {value_entered_float} rounded to 2 decimal places is {rounded_value}.")
print(f"The value without rounding is {squared_value}")
