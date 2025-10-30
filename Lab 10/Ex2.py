#Create the following lists:
# List of individuals' ages
#ages = [25, 30, 22, 35, 28, 40, 50, 18, 60, 45]


###Lists of individuals' names and genders
##names = ["Joe", "Jaden", "Max", "Sidney", "Evgeni", "Taylor", "Pia", "Luis", "Blanca", "Cyndi"]
#gender = ["M", "M", "M", "F", "M", "F", "F", "M", "F", "F"]

#Use zip() create a list of (age, gender) tuples.  

#Using Pandas, convert the list to a DataFrame, with names as the index and columns Age and Gender. Print out the dataframe and summarize the DataFrame using the describe() method.


#Calculate and print out the average age by gender

import pandas as pd

ages = [25, 30, 22, 35, 28, 40, 50, 18, 60, 45]
names = ["Joe", "Jaden", "Max", "Sidney", "Evgeni", "Taylor", "Pia", "Luis", "Blanca", "Cyndi"]
gender = ["M", "M", "M", "F", "M", "F", "F", "M", "F", "F"]

#Create dictionary from the lists

dict = zip(ages, gender)

#Convert dict to a dataframe with names as the keys
df = pd.DataFrame(dict, index=names, columns=["Age", "Gender"])
print(df)

summary = df.describe()
print(summary)

#Calculate average age by gender 

average_age_by_gender = df.groupby("Gender")["Age"].mean()
print("Average age by gender:")
print(average_age_by_gender)