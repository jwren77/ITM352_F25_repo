#
#Develop a program that will iterate through two tuples you create of your top 5 favorite celebrities and their corresponding ages (e.g. (“Taylor Swift”, “Lionel Messi”, “Max Verstappen”, “Keanu Reeves”, “Angelina Jolie”) and (35, 37, 27, 60, 49)). Then, append the values to two lists and store the lists as values in a dictionary with keys “celebrities” and “age"

celebrities_tuple = ("Taylor Swift", "Messi", "Reeves", "Jolie", "Verstappen")
ges_tuple = (34, 37, 60, 49, 27)

celebrities_list = []
ages = []

for celeb in celebrities_tuple:
    celebrities_list.append(ages)
for age in ages_tuple:
   ages_list.append(age)

celebrities_dictionary = {
    "celebrities": celebrities_list,
    "ages": ages_list
}

data = {"celebrities": list(names), "ages": list(ages)}
print(data)