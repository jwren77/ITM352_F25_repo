#string manipulation example

first = input("Enter first name: ")
middle_initial = input("Enter middle initial: ")
last = input("Enter last name: ")
#Using +
full_name = last + " " + first

print("Your full name is:", full_name)
#Using an f-string
print(f"Your full name is {first} {middle_initial}. {last}")
#Using % formatting
print("Your full name is %s %s. %s" % (first, middle_initial, last))
#Using str.format()
print("Your full name using format is : {} {}. {}".format(first, middle_initial, last))

#Using join()
print("Your full name the tuple version is " + " ".join([first, middle_initial + ".", last]))

# using forma() but unpacking a list
name_parts = [first, middle_initial + ".", last]
print("Your full name using unpacked list is : {} {}. {}".format(*name_parts))