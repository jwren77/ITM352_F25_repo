#create a function called midpoint that takes two numbers as input
#and returns the values halfway between them
#Name Joe Wren
#Date 9/10/2025

def midpoint(num1, num2):
    mid = (num1 + num2) / 2
    return mid

number1 = float(input("Please enter the first number: "))
number2 = float(input("Please enter the second number: "))
result = midpoint(number1, number2)
print(f"The midpoint between {number1} and {number2} is {result}.")