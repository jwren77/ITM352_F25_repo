#Write a program that takes the dictionary of quiz questions you created for Assignment 1 and saves it as a JSON file. 

import json

QUESTIONS = {
    "What is your name? ": ["name","James"],
    "How old are you? ": ["age","30"],
    "What is your favorite programming language? ": ["language","Python"]
}

with open('quiz_questions.json', 'w') as json_file:
    json.dump(QUESTIONS, json_file)

print("Quiz questions have been saved to quiz_questions.json")