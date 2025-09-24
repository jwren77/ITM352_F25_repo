#Create list of responses add response 0 add 6
#Name Joe Wren
#9/16/2025

#responses = [5, 7, 3, 8]
#responses.append(0)
#responses.insert(2, 6)
#print(responses)

responses = [5, 7, 3, 8]
responses.append(0)
print("After appending 0:", responses)
responses = responses[:2] + [6] + responses[2:]
print("After inserting 6 at index 2:", responses)
