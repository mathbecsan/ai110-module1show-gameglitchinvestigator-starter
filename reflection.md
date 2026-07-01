# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

The first time I ran `streamlit run app.py`, the app loaded and looked normal (title, sidebar difficulty selector, a text input, three buttons), but playing it quickly showed it was broken in several ways. Running `pytest` first, before touching anything, also failed all 3 starter tests immediately with `NotImplementedError`, because `logic_utils.py` only contains stub functions — none of the real logic (`check_guess`, `parse_guess`, `get_range_for_difficulty`, `update_score`) actually lives there yet; it's all still sitting in `app.py`.

Four concrete bugs I found:

1. **Hints are backwards.** When `check_guess` decides the outcome is `"Too High"`, the message it pairs with that outcome is `"📈 Go HIGHER!"` — the opposite of what a "too high" guess should tell you. Same problem in reverse for `"Too Low"` → `"📉 Go LOWER!"`.
2. **The secret number changes type every other attempt**, which is the "commitment issues" bug the README hints at. In `app.py`, on even-numbered attempts the code does `secret = str(st.session_state.secret)`, turning the secret into a string, while the guess stays an `int`. This breaks the `==` win check (an `int` can never equal a `str` in Python) and breaks the `>` comparison, which raises a `TypeError` that gets caught and silently falls back to comparing the guess and secret as **strings**, so `"9" > "50"` evaluates to `True` (comparing the characters `'9'` and `'5'`) even though `9 < 50`. This is the direct cause of "you can't win" — a correct guess submitted on an even attempt is never recognized as a win.
3. **"New Game" doesn't fully reset the game.** Clicking it resets `attempts` and `secret`, but never resets `st.session_state.status`. So after winning or losing once, `status` stays `"won"`/`"lost"` forever, and the very next line of the app (`if st.session_state.status != "playing": ... st.stop()`) immediately halts the app again — "New Game" is effectively a dead button after your first win/loss.
4. **Score changes are inconsistent for the same outcome.** In `update_score`, a `"Too High"` guess adds `+5` to the score on even-numbered attempts but subtracts `-5` on odd-numbered attempts — the same mistake (guessing too high) is sometimes rewarded and sometimes punished depending on parity of the attempt count, which looks like the score randomly jumping around.

**Bug Reproduction Log**

I reproduced these directly by calling the functions as currently written in `app.py` (not by guessing at the behavior) — real console output below.

| Input | Expected Behavior | Actual Behavior | Console Error / Output |
|-------|-------------------|-----------------|------------------------|
| `check_guess(60, 50)` | Outcome "Too High" with a hint telling the player to guess **lower** | Outcome `"Too High"` paired with message `"📈 Go HIGHER!"` — hint contradicts the outcome | `('Too High', '📈 Go HIGHER!')` |
| `check_guess(40, 50)` | Outcome "Too Low" with a hint telling the player to guess **higher** | Outcome `"Too Low"` paired with message `"📉 Go LOWER!"` — hint contradicts the outcome | `('Too Low', '📉 Go LOWER!')` |
| Guess `9` vs secret `50`, on an even attempt (secret gets stringified to `"50"` by `app.py`) | Outcome "Too Low" (since 9 < 50) | Outcome `"Too High"` — wrong, because `"9" > "50"` compares the strings character-by-character (`'9' > '5'`), not the numbers | `('Too High', '📈 Go HIGHER!')` |
| Win the game, then click "New Game 🔁" | Game resets and lets you submit a new guess | App immediately re-shows "You already won. Start a new game to play again." and calls `st.stop()` because `status` was never reset to `"playing"` | No exception — just a soft-lock; confirmed by reading `app.py:134-145` |
| `pytest tests/` (before any fix) | Starter tests for `check_guess` pass | All 3 tests fail | `NotImplementedError: Refactor this function from app.py into logic_utils.py` (raised from `logic_utils.py:21`) |

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
