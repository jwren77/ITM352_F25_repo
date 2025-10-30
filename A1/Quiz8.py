import random

# Ask for student ID
student_id = input("Enter your student ID: ")

# Use the ID to make the random results consistent
random.seed(int(student_id))

# Generate two numbers between 1 and 10
num1 = random.randint(1, 10)
num2 = random.randint(1, 10)

print(f"Your two numbers are: {num1} and {num2}")