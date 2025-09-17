#creat module with handy math functions
#joe
#9/10/2025

#function to compute square root
def midpoint(a, b):
    return (a + b) / 2

def squareroot(n):
    return n ** 0.5

def exponent(base, exp):
    return base ** exp

# Shadowing built-ins on purpose for the lab
def max(a, b):
    return a if a >= b else b

def min(a, b):
    return a if a <= b else b

def apply2(x, y, func):
    # func must be a function that accepts (x, y)
    return f"The function {func.__name__} {x},{y} = {func(x, y)}"