import random

# Step 6 – Randomize question order and answer order
# ---------------------------------------------------

# Each question's FIRST answer is the correct one
questions = {
    "What is the airspeed of an unladen swallow in miles/hr": [
        "12", "8", "11", "15"
    ],
    "What is the capital of Texas": [
        "Austin", "San Antonio", "Dallas", "Waco"
    ],
    "The Last Supper was painted by which artist": [
        "Da Vinci", "Rembrandt", "Picasso", "Michelangelo"
    ],
    "Which classic novel opens with the line 'Call Me Ishmael'?": [
        "Moby Dick", "Wuthering Heights", "The Old Man and the Sea", "The Scarlet Letter"
    ],
    "Frank Lloyd Wright designed a house that included a waterfall. What is the name of this house?": [
        "Fallingwater", "Watering Heights", "Mossyledge", "Taliesin"
    ]
}

# Shuffle the question order
question_list = list(questions.items())
random.shuffle(question_list)

score = 0

for q, answers in question_list:
    correct = answers[0]              # the first one is correct
    random.shuffle(answers)           # mix the order of answers

    print("\n" + q + "?")
    for i, choice in enumerate(answers):
        print(f"{i + 1}. {choice}")

    while True:
        user = input("Pick 1-4: ")
        if user.isdigit() and 1 <= int(user) <= 4:
            if answers[int(user) - 1] == correct:
                print("✅ Correct!")
                score += 1
                break
            else:
                print("❌ Wrong! Try again.")
        else:
            print("Please enter a number between 1 and 4.")

print("\nQuiz finished!")
print("Your total score:", score, "/", len(question_list))