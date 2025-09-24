#start with empty shopping list
#Name Joe Wren
#Date 9/17/2025

shopping_list = []
shopping_list.append("apples")
shopping_list.append("bananas")
shopping_list.append("carrots")
shopping_list.insert(0, "milk")
print("Your shopping list contains:", shopping_list)

shopping_list.pop()
print("After removing the last item, your shopping list contains:", shopping_list)