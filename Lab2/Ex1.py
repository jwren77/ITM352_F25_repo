# Ask the user to enter a number between 1 and 100. 
# Square the number and print the result.
#Joseph Wren
#Date: 9/3/25


print("Hi there")
value_entered = input("Please enter a number between 1 and 100: ")
print("The user entered:", value_entered)
value_as_integer = int(value_entered)
value_squared = value_as_integer ** 2
print("The number squared is:", value_squared)
input("Press Enter to exit...")