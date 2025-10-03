#determine where a list of purchases is within our budget or not(e.g. recent_purchases = [36.13, 23.87, 183.35, 22.93, 11.62]) and set a budget for yourself (e.g. $50). Print the message “This purchase is over budget!” if the expense is greater than your budget and “This purchase is within budget” otherwise.

#Joe Wren

recent_purchases = [36.13, 23.87, 183.35, 22.93, 11.62]
budget = 50
total_spent = 0
for purchase in recent_purchases:
    total_spent += purchase
if total_spent > budget:
    print(f"You have spent ${total_spent:.2f}, which is over budget! and that is over your budget of ${budget}.")
else:
    print(f"You have spent ${total_spent:.2f}, which is within budget and that is under your budget of ${budget}.")


