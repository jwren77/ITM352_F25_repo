#Scrape data from the city of Chicago's data portal

import urllib.request
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

url = "https://data.cityofchicago.org/Historic-Preservation/Landmark-Districts/zidz-sdfj/about_data"

#Open the web page

print("Opening URL...", url)
webpage = urllib.request.urlopen(url)


#Iterate through each line and search for title tags
for line in webpage:
    line = line.decode("utf-8")  #Decode the binary data to text
    if "<title>" in line:
        print(line)