def determine_progress3(hits, spins):
    if spins == 0 or (hits / spins) <= 0:
        return "Get going!"
    elif (hits / spins) >= 0.5 and (hits < spins):
        return "You win!"
    elif (hits / spins) >= 0.25:
        return "Almost there!"
    else:
        return "On your way!"