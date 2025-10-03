def determine_progress2(hits, spins):
    if spins == 0:
        return "Get going!"
    ratio = hits / spins
    if ratio <= 0:
        return "Get going!"
    if (ratio >= 0.5) and (hits < spins):
        return "You win!"
    if ratio >= 0.25:
        return "Almost there!"
    return "On your way!"