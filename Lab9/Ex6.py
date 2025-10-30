#read a file of questions from a json file and save them in a dictionary
#and then print the dictionary to the console
import json

#specify the json file name
json_filename = 'quiz_questions.json'
#open the json file and read the data
with open(json_filename, 'r') as json_file:
    data = json.load(json_file)

#print the data to the console
print(data)
