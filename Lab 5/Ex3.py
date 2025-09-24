#Go back to the List lab where you appended a tuple of respondent ID values (1012, 1035, 1021, and 1053) list of survey response values (5, 7, 3, and 8) to get [5, 7, 3, 8, (1012, 1035, 1021, and 1053)]. We determined that this was a poor design for managing the survey data.  Rather than doing this, create a Dictionary with ID values as the keys and survey responses as the values using zip(). Your dictionary should look like {1012: 5, 1035: 7, 1021: 3, 1053: 8}
#name Joe Wren
survey_responses = [5, 7, 3, 8]

#define a tuple of respondent ID values
respondent_ids = (1012, 1035, 1021, 1053)
#use zip to create a dictionary with ID values as the keys and survey responses as the values
survey_dict = dict(zip(respondent_ids, survey_responses))
print('Survey Dictionary:', survey_responses)
print('Survey Dictionary:', survey_dict)
print('Survey Dictionary:', survey_dict)

print(f"Respondent {respondent_ids[2]} gave a survey response of {survey_dict[respondent_ids[2]]}")
