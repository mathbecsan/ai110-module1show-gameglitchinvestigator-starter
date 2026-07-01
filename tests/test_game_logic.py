from logic_utils import check_guess, get_hint_message

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result == "Too Low"

# --- Regression tests for Bug 1: hint messages were swapped ---

def test_too_high_hint_tells_player_to_go_lower():
    # A guess of 60 against secret 50 is "Too High", so the message
    # must tell the player to go LOWER, not higher.
    message = get_hint_message("Too High")
    assert message == "📉 Go LOWER!"

def test_too_low_hint_tells_player_to_go_higher():
    # A guess of 40 against secret 50 is "Too Low", so the message
    # must tell the player to go HIGHER, not lower.
    message = get_hint_message("Too Low")
    assert message == "📈 Go HIGHER!"

# --- Regression test for Bug 2: secret was stringified on even attempts ---

def test_low_guess_against_larger_secret_is_never_too_high():
    # Old bug: when the secret was stringified (e.g. "50") and compared
    # against an int guess, "9" > "50" was True as a STRING comparison
    # (comparing the characters '9' and '5'), wrongly reporting "Too High"
    # for a guess that's actually far too low. With both values kept as
    # ints, this must always resolve correctly as "Too Low".
    result = check_guess(9, 50)
    assert result == "Too Low"
