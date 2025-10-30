with open("names.txt", "r") as file_object:
    print(type(file_object))
    content = file_object.read()
    print(content)

