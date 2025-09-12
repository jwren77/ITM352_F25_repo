#creat module with handy math functions
#joe
#9/10/2025

#function to compute square root
def square_root(x, precision=2):
    if x < 0:
        raise ValueError("Cannot compute square root of a negative number.")
    return x ** 0.5
number = float(input("Enter a number to find its square root: "))
result = square_root(number)
print(f"The square root of {number} is approximately {result:.2f}.")

#function for midpoint
def midpoint(num1, num2):
    mid = (num1 + num2) / 2
    return mid

number1 = float(input("Please enter the first number: "))
number2 = float(input("Please enter the second number: "))
result = midpoint(number1, number2)
print(f"The midpoint between {number1} and {number2} is {result}.")
#exponent function
def exponent(base, exp):
    return base ** exp
#max
def max(a, b):
    if a > b:
        return a
    else:
        return b
    
#min
def min(a, b):
    if a < b:
        return a
    else:
        return b
