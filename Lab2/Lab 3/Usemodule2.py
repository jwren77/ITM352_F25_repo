# Test to see how the functions defined in HandyMath work
# Joseph Wren
# Date 9/12/2025

from HandyMath import handy_max, handy_min  # Use unique names to avoid conflict with built-ins


number1 = float(input("Please enter the first number: "))
number2 = float(input("Please enter the second number: "))

max_number = handy_max(number1, number2)
print(f"The max between {number1} and {number2} is {max_number}")

min_number = handy_min(number1, number2)
print(f"The min between {number1} and {number2} is {min_number}")

print(handy_max)
print(handy_min)

