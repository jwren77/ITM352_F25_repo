def determine_progress_no_if(hits, spins):
    
    ratio = (hits / spins) if (spins != 0) else float("-inf")

    g0 = (spins == 0) or (ratio <= 0)
    win = (ratio >= 0.5) and (hits < spins)
    almost = (ratio >= 0.25)

    index = (not g0) * 1 + (not g0 and almost) * 1 + (not g0 and win) * 1
    messages = ["Get going!", "On your way!", "Almost there!", "You win!"]
    return messages[index]