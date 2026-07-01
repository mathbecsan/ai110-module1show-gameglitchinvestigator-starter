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

I used **Claude Code** (Anthropic's AI coding assistant, running in my editor) as the primary AI teammate for this project, working file-by-file across `app.py`, `logic_utils.py`, and `tests/test_game_logic.py`.

**Correct suggestion:** After I marked the secret-stringification bug with a `# FIXME` comment in `app.py`, I asked the AI to trace where `check_guess`'s `TypeError` fallback branch was actually being exercised. It correctly identified that the `try/except TypeError` block in the original `check_guess` only existed to paper over `app.py` sometimes passing a stringified secret — and that the *real* fix was to stop stringifying the secret at the call site in `app.py`, not to keep patching `check_guess` to tolerate mixed types. I verified this was correct two ways: (1) I wrote a regression test, `test_low_guess_against_larger_secret_is_never_too_high`, asserting `check_guess(9, 50) == "Too Low"` — before the fix this case produced `"Too High"` because `"9" > "50"` is `True` as a string comparison; after the fix it passes; (2) I ran `streamlit run app.py` and confirmed the app starts without errors and the "Attempts left"/win logic no longer depends on attempt parity.

**Incorrect/misleading suggestion:** My first instinct (and the AI's first suggested approach) was to "just move `check_guess` into `logic_utils.py` unchanged" as part of the refactor step. That looked reasonable, but running `pytest` against the *starter* tests immediately showed it was wrong: the starter tests assert `check_guess(50, 50) == "Win"` (a plain string), while the original `app.py` version of `check_guess` returns a **tuple** `("Win", "🎉 Correct!")`. A tuple is never `== "Win"`, so a literal "just move it" refactor would have kept every starter test failing, just with a different error message than the `NotImplementedError` we started with. I caught this by actually running `pytest tests/ -v` and reading the failure instead of assuming the move was done once the import worked. The real fix was to split the function: `check_guess` now returns only the outcome string (matching what the tests expect), and a new `get_hint_message(outcome)` function separately maps the outcome to its display text — which is also where the swapped hint-text bug got fixed.

---

## 3. Debugging and testing your fixes

I treated "fixed" as meaning three things had to all be true at once: the specific regression test for that bug passes, the full `pytest` suite still passes (so the fix didn't break anything else), and the live Streamlit app starts and behaves sanely for that scenario. Before any fix, `pytest tests/ -v` failed all 3 starter tests with `NotImplementedError` (the stub functions in `logic_utils.py` hadn't been implemented yet). After refactoring the real logic into `logic_utils.py` and fixing the two targeted bugs, I re-ran `pytest tests/ -v` and got `6 passed in 0.01s` — the 3 original starter tests plus 3 new regression tests I added (`test_too_high_hint_tells_player_to_go_lower`, `test_too_low_hint_tells_player_to_go_higher`, `test_low_guess_against_larger_secret_is_never_too_high`). I also started the app with `streamlit run app.py --server.headless true` and confirmed with `curl` that it returns `HTTP 200` with no traceback in the server log, which told me the import refactor (`from logic_utils import ...`) didn't break anything at the app level, not just at the unit-test level. The AI helped design the regression tests by pointing at the exact `check_guess`/`get_hint_message` output that was wrong *before* the fix (e.g., `check_guess(9, 50)` returning `"Too High"` instead of `"Too Low"`), so each new test directly encodes "this specific wrong output must never come back" rather than testing something vague.

---

## 4. What did you learn about Streamlit and state?

Streamlit doesn't work like a normal app that keeps running in the background waiting for the next click — instead, every single time you interact with a widget (click a button, type in a text box, check a checkbox), Streamlit throws away the current run and **re-executes your entire script from top to bottom**. That's the "rerun" model. Because of that, any plain Python variable would just reset to its initial value on every click — which is exactly why `st.session_state` exists: it's a dictionary-like object that Streamlit keeps alive *across* reruns, so things like the secret number, the attempt count, and the score can persist while the rest of the script re-runs fresh each time. This project made that concrete: the "New Game" bug happened precisely because one piece of state (`status`) was left out of the reset, so on the very next rerun the script re-read that stale value from `session_state` and immediately hit the `st.stop()` branch — a good reminder that in Streamlit, "did I update session_state" matters more than "did I update a local variable."

---

## 5. Looking ahead: your developer habits

One habit I want to keep: **write a regression test that encodes the actual wrong output you saw**, not just a generic "does this function work" test. For example, `check_guess(9, 50)` really did return `"Too High"` before the fix — turning that exact case into a permanent test is a much stronger guardrail than a vague assertion, because it will fail loudly if the old bug's root cause (mixed int/str comparisons) ever creeps back in.

One thing I'd do differently next time: verify a refactor against the *existing* test suite before trusting that "the code compiles/imports" means "the code is correct." My first pass at moving `check_guess` into `logic_utils.py` kept its original tuple return type, which looked fine until I actually ran `pytest` and saw it still failed the starter tests for a completely different reason than before. Running the tests earlier in the process, not just at the end, would have caught that mismatch sooner.

This project changed how I think about AI-generated code mainly around **trusting output type/shape without checking call sites**. The starter `check_guess` and the starter tests were both "AI-generated" but disagreed with each other about what the function should return — a subtle inconsistency that's easy to miss just by reading either file in isolation, but obvious the moment you actually run the test suite. It reinforced that "the code looks reasonable" and "the code is correct" are different claims, and only running it (tests, then the live app) closes that gap.
