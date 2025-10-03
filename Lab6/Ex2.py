listofLists = [[],[1]*3, [2]*7, [3]*12]
print(listofLists)

listnumber = int(input("Enter a list number (0-3): "))
listLength = len(listofLists[listnumber])

listLength = listofLists[listnumber]
if listLength > 5:
    print(f"User entered {listnumber}: Short list")
elif 5<= listLength <= 10:
    print(f"User entered {listnumber}: Medium list")
else:
    print(f"User entered {listnumber}: Long list")

# 2c
test_lists = [
    [], [1,2,3,4],                 # < 5
    [1,2,3,4,5], list(range(10)),  # 5..10
    list(range(11)), list(range(25))  # > 10
]

expected = [
    "Fewer than 5 elements", "Fewer than 5 elements",
    "Between 5 and 10 elements (inclusive)", "Between 5 and 10 elements (inclusive)",
    "More than 10 elements", "More than 10 elements"
]

for items, want in zip(test_lists, expected):
    got = describe_list_size(items)
    assert got == want, f"Failed for len={len(items)}: got {got}, want {want}"
print("2c tests passed.")