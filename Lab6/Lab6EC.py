def movie_price(age, weekday, matinee):
    prices = [14]  

    
    if age >= 65:
        prices.append(8)


    if weekday.strip().lower() == "tuesday":
        prices.append(10)


    if matinee:
        prices.append(5 if age >= 65 else 8)

    return min(prices)


def show_price(age, weekday, matinee):
    print(f"age={age}, weekday='{weekday}', matinee={matinee} -> ${movie_price(age, weekday, matinee)}")

show_price(30, "Monday", False)     
show_price(70, "Monday", False)    
show_price(30, "Tuesday", True)     