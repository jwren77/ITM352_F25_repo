def determine_progress1(hits, spins):
    if spins == 0:
        return "Get going!"
    
    hits_spins_ratio = hits / spins

    if hits_spins_ratio > 0:
        progress = "On your way!"
        if hits_spins_ratio >= 0.25:
            progress = "Almost there!"
            if hits_spins_ratio >= 0.5:
                if hits < spins:
                    progress = "You win!"
    else:
        progress = "Get going!"

    return progress


def test_determine_progress(progress_function):   # fixed typo here
    assert progress_function(0, 0) == "Get going!"
    assert progress_function(1, 4) == "On your way!"
    assert progress_function(1, 3) == "Almost there!" 
    assert progress_function(2, 4) == "Almost there!"
    assert progress_function(2, 3) == "You win!"
    assert progress_function(3, 4) == "You win!"
    assert progress_function(3, 3) == "Get going!"
    assert progress_function(4, 3) == "Get going!"   
    assert progress_function(0, 3) == "Get going!"

    print("All tests passed ")


# Run the tests
test_determine_progress(determine_progress1)