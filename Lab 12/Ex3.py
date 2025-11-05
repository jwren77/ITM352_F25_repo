#Parse the UH Shidler ITM dept page and extract faculty names

import urllib.request
from bs4 import BeautifulSoup

itm_url = "https://shidler.hawaii.edu/itm/people"

print("Please wait while we open URL...", itm_url)
#Open URL
itm_html = urllib.request.urlopen(itm_url)
# use beautifulsoup to open page and parse it
html_to_parse = BeautifulSoup(itm_html, "html.parser")

pretty_html = html_to_parse.prettify()
line = pretty_html.splitlines()
num_to_print = 10

#print the first few lines of the pretty html
for line in line[:num_to_print]:
    print(line)

#find and print just the faculty names
list_of_ITM_faculty = html_to_parse.find_all("h2", class_="title")
#create a list with just the names
itm_faculty = []
for element in list_of_ITM_faculty:
    itm_faculty.append(element.text)
    print(element.text)

print("Number of ITM faculty found:", len(itm_faculty))

unique_itm_faculty = list(set(itm_faculty))
print("Number of unique ITM faculty found:", len(unique_itm_faculty))