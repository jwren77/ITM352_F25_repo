# Ask the user to enter afloating point number 100. 
# Square the number and print the result.
#Joseph Wren
#Date: 9/3/25


print("Hi there")
value_entered = input("Please enter a number between 1 and 100: ")
print("The user entered:", value_entered)
value_as_float= float(value_entered)

value_squared = value_as_float**2
print(f"The value squared is: {value_squared}")

# Ask the user to enter a floating point number between 1 and 100
# Square the number and print the result rounded to 2 decimal places
# Joseph Wren
# Date: 9/3/25

print("Hi there")
value_entered = input("Please enter a number between 1 and 100: ")
print("The user entered:", value_entered)
value_as_float = float(value_entered)

value_squared = value_as_float * value_as_float
value_squared_rounded = round(value_squared, 2)
print(f"The value squared is: {value_squared_rounded}")