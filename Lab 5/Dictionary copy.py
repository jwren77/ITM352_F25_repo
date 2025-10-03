#creat a dictionary

country_captials = {
    "USA": "Washington DC",
    "India": "New Delhi",
    "China": "Beijing", 
    "Russia": "Moscow"}

print(country_captials)

#Acces value by key

print(country_captials["India"])
print(country_captials["USA"])

country_captials["Germany"] = "Berlin"
print(country_captials)

#del country_captials["Russia"]
#print(country_captials)
#print length of dictionary

print(len(country_captials))
#print germany in dictionary
print('Germany' in country_captials)
print('France' in country_captials)