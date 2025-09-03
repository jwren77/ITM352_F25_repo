#ask the user for their birth year . Calculate their age by subtracting
#it from the current year (2025). Print their age.
#Joseph Wren
#Date: 9/3/25

birth_year = input("Please enter your birth year as a four digit number (YYYY): ")
birth_year_int = int(birth_year)
      #This should be changed to extract the year automatically for the current date
      #THis doesnt take into account day or month. Fix later
current_year = 2025
age = current_year - birth_year_int
print("You entered:", birth_year)
print("Your age is:", age)
