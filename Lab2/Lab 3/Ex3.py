def square_root(x):
    if x < 0:
        raise ValueError("Cannot compute square root of a negative number.")
    return x ** 0.5
number = float(input("Enter a number to find its square root: "))
result = square_root(number)
print(f"The square root of {number} is approximately {result:.2f}.")