#Define a list of survery response values (5, 7, 3, 8)
#Store them in a variable define a tuple of response ids (1012, 1035, 1021, 1053)
#Store them in a variable
#Joe Wren9/17

#survey_responses = [5, 7, 3, 8]
#print(len(survey_responses))
#response_ids = (1012, 1035, 1021, 1053)
#print(len(response_ids))
#survey_responses.append(response_ids)
#print(survey_responses)

response_values = [(1012,5), (1035,7), (1021,3), (1053,8)]
response_values.sort()
print("Sorted by response ID:", response_values)
