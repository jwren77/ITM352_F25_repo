# Personal info 
age = 23
weekly_spending = 300
gpa = 3.5
birth_year = 2002
grad_year = 2026
current_year = 2025

# Required practice calculations
print("Age in days:", age * 365)
print("Monthly expenses:", weekly_spending * 52 / 12)
print("Hours alive:", age * 365 * 24)
print("GPA on 100-point scale:", gpa * 25)

# 5 more expressions using personal numbers
print("Years until graduation:", grad_year - current_year)
print("Age at graduation:", age + (grad_year - current_year))
print("Years since birth:", current_year - birth_year)
print("Weeks alive:", age * 52)
print("Decades old:", age / 10)

# Statistic: Amount of gum chewed in the last year (10 sticks/week)
gum_per_week = 10
weeks_in_year = 52
gum_chewed = gum_per_week * weeks_in_year
print("Sticks of gum chewed in the last year:", gum_chewed)

# Pause at the end so output stays visible
# Personal Information
name = "Your Name"
hometown = "Kapolei"
major = "MIS"
student_id = 30092206
age = 23

print(f"My name is {name} and I’m {age} years old.")
print(f"I’m from {hometown} and studying {major}.")
print(f"My student ID check digit is {student_id % 9}.")
years_until_grad = grad_year - 2025
print(f"Years until graduation: {years_until_grad}")
print(f"Age at graduation: {age + years_until_grad}")
is_adult = age >= 18
print("Am I an adult?", is_adult)
username = name.lower()[:3] + str(student_id % 100)
print("My username:", username)