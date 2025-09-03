def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

def multiply(x, y):
    return x * y

def divide(x, y):
    try:
        return x / y
    except ZeroDivisionError:
        return "Error: Division by zero is not allowed."

def main():
    print("Simple Calculator")
    # Test cases to try:
    # 1. Addition: 5, 3, choose 1 (expect 8.0)
    # 2. Subtraction: 10, 4, choose 2 (expect 6.0)
    # 3. Multiplication: 7, 6, choose 3 (expect 42.0)
    # 4. Division: 20, 4, choose 4 (expect 5.0)
    # 5. Division by zero: 8, 0, choose 4 (expect error message)
    # 6. Invalid operation: 2, 2, choose 5 (expect error message)
    # 7. Non-numeric input: a, 2 or 2, b (expect error message)
    try:
        num1 = float(input("Enter the first number: "))
        num2 = float(input("Enter the second number: "))
    except ValueError:
        print("Invalid input. Please enter numeric values.")
        return

    print("Select operation:")
    print("1. Add")
    print("2. Subtract")
    print("3. Multiply")
    print("4. Divide")

    choice = input("Enter choice (1/2/3/4): ")

    if choice == '1':
        result = add(num1, num2)
        op = '+'
    elif choice == '2':
        result = subtract(num1, num2)
        op = '-'
    elif choice == '3':
        result = multiply(num1, num2)
        op = '*'
    elif choice == '4':
        result = divide(num1, num2)
        op = '/'
    else:
        print("Invalid operation choice.")
        return

    print(f"{num1} {op} {num2} = {result}")

if __name__ == "__main__":
    main()


