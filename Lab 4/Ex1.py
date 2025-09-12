#string manipulation example

first = input("Enter first name: ")
middle_initial = input("Enter middle initial: ")
last = input("Enter last name: ")
full_name = last,  + " " + first

print("Your full name is:", full_name)

print(f"Your full name is {first} {middle_initial}. {last}")
