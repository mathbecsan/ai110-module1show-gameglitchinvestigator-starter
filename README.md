# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

**Game's purpose:** A Streamlit number-guessing game. Pick a difficulty (Easy/Normal/Hard, each with its own number range and attempt limit), and try to guess the secret number within the attempt limit, using "Too High"/"Too Low" hints and a running score to guide you.

**Bugs found** (see `reflection.md` section 1 for full reproduction log):
1. Hint messages were swapped — a "Too High" outcome told you to "Go HIGHER!" instead of lower, and vice versa.
2. The secret number was silently converted to a string on every even-numbered attempt, which broke both the win check (`int == str` is never `True`) and the high/low comparison (fell back to a `TypeError`-caught string comparison, e.g. `"9" > "50"` is `True` lexicographically).
3. The "New Game" button reset the secret and attempt count but never reset `status`, `score`, or `history`, so the app soft-locked on the "you already won/lost" screen after your first game.
4. `update_score` gave `+5` instead of `-5` for a "Too High" guess on even-numbered attempts, making the score look like it randomly jumped around for the same mistake.

**Fixes applied:**
- Refactored `get_range_for_difficulty`, `parse_guess`, `check_guess`, and `update_score` out of `app.py` and into `logic_utils.py`.
- Fixed `check_guess` to return a plain outcome string (`"Win"`/`"Too High"`/`"Too Low"`) instead of a tuple, matching what the starter tests expect, and split hint-message formatting into a new `get_hint_message(outcome)` function with the correct (un-swapped) text.
- Removed the secret-stringification logic in `app.py` so the guess and secret are always compared as the same type (`int`).
- Fixed "New Game" to reset `status`, `score`, and `history` in addition to `attempts` and `secret`, and to use the selected difficulty's range instead of a hardcoded `1-100`.
- Added 3 new `pytest` regression tests targeting the swapped-hint bug and the type-mismatch bug.

## 📸 Demo Walkthrough

1. User selects "Normal" difficulty in the sidebar (range 1–100, 8 attempts allowed).
2. User enters a guess of `40` and clicks "Submit Guess 🚀" → game returns outcome "Too Low" with hint "📈 Go HIGHER!" (correct direction).
3. User enters a guess of `70` → outcome "Too High" with hint "📉 Go LOWER!" (correct direction — this is the bug that used to be backwards).
4. Score updates after each guess (`update_score` runs on every submit, visible in the "Developer Debug Info" expander).
5. User enters the correct guess, e.g. `55` → outcome "Win", the app shows 🎈 balloons and a "You won!" message with the final score, and `status` is set to `"won"`.
6. User clicks "New Game 🔁" → the secret, attempts, score, history, and status all reset, and the game is immediately playable again (this used to soft-lock before the fix).

**Screenshot** *(optional)*: <!-- Insert a screenshot of your fixed, winning game here -->

## 🧪 Test Results

```
$ python3 -m pytest tests/ -v
============================= test session starts ==============================
platform darwin -- Python 3.12.0, pytest-9.1.1, pluggy-1.6.0
collecting ... collected 6 items

tests/test_game_logic.py::test_winning_guess PASSED                      [ 16%]
tests/test_game_logic.py::test_guess_too_high PASSED                     [ 33%]
tests/test_game_logic.py::test_guess_too_low PASSED                      [ 50%]
tests/test_game_logic.py::test_too_high_hint_tells_player_to_go_lower PASSED [ 66%]
tests/test_game_logic.py::test_too_low_hint_tells_player_to_go_higher PASSED [ 83%]
tests/test_game_logic.py::test_low_guess_against_larger_secret_is_never_too_high PASSED [100%]

============================== 6 passed in 0.01s ===============================
```

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, describe the Enhanced UI changes here — a screenshot is optional]
