def isLeapYear(year):
    if (year % 400) == 0:
        return "Leap year"
    if (year % 100) == 0:
        return "Not a leap year"
    if (year % 4) == 0:
        return "Leap year"
    return "Not a leap year"


print(isLeapYear(birth_year))
print(isLeapYear(closest_leap))