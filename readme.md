# Interactive Stand Game - RPi5 & Kivy: Comprehensive Project Documentation

## Project Overview
This is a high-performance, interactive game application for a brand convention stand, built on Raspberry Pi 5 using Python 3 and Kivy framework. It integrates touchscreen GUI with physical hardware (12 arcade buttons and LEDs via relays) for a dual-mode experience: **Agility Game** (reaction-time button pressing) and **Quiz Game** (brand knowledge multiple-choice). The game measures player performance, computes scores (agility: 1000 - ms reaction; quiz: +500 per correct), and maintains a local leaderboard in JSON. Designed for unattended, high-traffic use: low-latency (<50ms input response), stable (non-blocking event-driven), modular (strict SoC). Total flow: Welcome -> Agility Instructions -> 5 Agility Rounds -> Quiz Instructions -> 3 Quiz Rounds -> Score Submission -> Leaderboard. Current status: Feature-complete (Phase 3), pending UI polish (Phase 4: virtual keyboard, attract mode). Insights: Prioritizes player immersion via sensory feedback (sounds, animations); zero-hack policy ensures maintainability for on-site tweaks.

**Key Metrics/Constraints:**
- Hardware: 12 buttons (input), 12 LEDs (output via active-low relays).
- Scoring: Agility (reaction-based, max 1000pts/round), Quiz (fixed 500pts/correct).
- Data: 5+ sample questions; top 15 leaderboard entries.
- Environment: Raspberry Pi OS, fullscreen kiosk mode, vertical orientation.
- Dependencies: Kivy (UI/multi-touch), gpiozero (GPIO abstraction), lgpio (RPi5 GPIO backend).

## Architecture Principles
The system follows a **Finite State Machine (FSM)**-driven architecture with **Separation of Concerns (SoC)**: 
- **FSM Core**: `GameManager` orchestrates states (e.g., 'agility', 'quiz') without UI/hardware coupling.
- **Event-Driven**: Kivy's `Clock` schedules non-blocking events (no `time.sleep()`); gpiozero callbacks handle inputs asynchronously to keep UI responsive.
- **Modularity**: UI (views only), Logic (FSM coordination), HAL (hardware abstraction), Data (persistence service).
- **Config-Driven**: All pins/timings/paths in `config.py`; no magic numbers.
- **Reliability**: Atomic JSON writes; GPIO cleanup on exit; error handling for missing files (defaults to empty).
- **Insights**: This prevents race conditions in multi-round games; enables easy testing (e.g., mock hardware). For AI analysis: Trace flow via `GameManager.go_to_screen()` calls; simulate states by inspecting `self.instruction_state`.

**High-Level Flow Diagram (Textual):**
```
WelcomeScreen -> show_instructions('agility') -> AgilityGameScreen (5 rounds via start_agility_round/on_button_press) -> end_agility_section -> show_instructions('quiz') -> QuizGameScreen (3 rounds via start_quiz_round/check_answer) -> end_game -> ScoreScreen -> submit_score -> LeaderboardScreen -> return_to_welcome
```

## Core Modules Breakdown
Categorized by responsibility. Each includes classes, methods/functions with params, returns, usage comments, and insights.

### 1. Entry Point & App Initialization (`app/__main__.py`)
- **Class: `GameApp(App)`** - Main Kivy application; inherits `kivy.app.App`.
  - **Method: `build(self)`** - Initializes UI and FSM. Loads `screens.kv`; creates `ScreenManager` with screens (Welcome, Instructions, AgilityGame, QuizGame, Score, Leaderboard); instantiates `GameManager(sm)`; returns `sm`. Usage: Called on app start; ensures fullscreen/borderless via `Config.set()`. Insight: Pre-import env vars (`SDL_AUDIODRIVER='alsa'`) fix RPi audio hangs; FadeTransition (0.4s) for smooth UX.
  - **Method: `on_stop(self)`** - Cleanup hook. Calls `self.game_manager.cleanup()`. Usage: Triggers on app close (Ctrl+C or exit); ensures GPIO release. Insight: Prevents resource leaks in long-running kiosk mode.
- **Command: `if __name__ == '__main__': GameApp().run()`** - Launches app. Usage: `python -m app` from root. Insight: Modular entry; virtual env recommended.

### 2. Game State Machine (`app/game_manager.py`)
- **Class: `GameManager`** - Central FSM controller; initializes services (HardwareController, DataManager, AudioManager); manages score, rounds, timers.
  - **Init: `__init__(self, screen_manager: ScreenManager)`** - Sets `self.sm`, `self.hw`, `self.dm`, `self.am`; loads questions; sets button callback; initializes state vars (score=0, rounds=5/3, timers). Usage: Passed from `GameApp.build()`; prints init confirmation. Insight: Loads all questions upfront for random sampling; tracks `agility_in_progress`/`quiz_in_progress` to ignore invalid inputs.
  - **Method: `start_game(self)`** - Resets state (score=0, rounds=0); plays 'start' sound; transitions to 'agility_game'; calls `start_countdown()`. Usage: From Instructions button. Insight: Ensures fresh state per player; enforces 5 agility + 3 quiz structure.
  - **Method: `start_countdown(self, dt=None)`** - Schedules 3-2-1-'VAI!' animation (scale 1.5->1.0, opacity fade-in instruction); plays sounds; schedules `start_agility_round(0.5s)`. Usage: Post-instructions. Insight: Uses `Clock.schedule_interval/update` for non-blocking; Portuguese text for localization.
  - **Method: `start_agility_round(self, dt=None)`** - Increments round; updates UI labels; hides countdown; picks random LED (0-11); turns on via `hw`; starts timer (`perf_counter()`); sets `agility_in_progress=True`. Usage: Chained after button press (0.5s delay). Insight: Caps at 5 rounds -> `end_agility_section()`; reaction scoring in callback.
  - **Method: `on_button_press(self, pressed_index)`** - Callback from HAL; if in progress, stops LED/timer; scores (1000 - ms if correct, else 0); plays sound; schedules next round (0.5s). Usage: Triggered by physical buttons. Insight: Only for agility; ignores wrong presses but penalizes time; prints for debugging.
  - **Method: `end_agility_section(self)`** - Turns off LEDs; sets `instruction_state='quiz'`; updates InstructionsScreen content; transitions. Usage: After 5 rounds. Insight: Bridges sections; custom body text explains quiz rules.
  - **Method: `start_quiz_section(self)`** - Samples 3 questions; transitions to 'quiz_game'; schedules `start_quiz_round(0.5s)`. Usage: From quiz instructions button. Insight: Error if <3 questions; random.sample ensures no repeats.
  - **Method: `start_quiz_round(self, dt=None)`** - Gets next question; calls `display_question()` on screen; sets `quiz_in_progress=True`; increments round. Usage: Chained after answer (2s delay). Insight: Caps at 3 -> `end_game()`; clears feedback.
  - **Method: `check_answer(self, selected_answer: str)`** - If in progress, compares to correct; adds 500pts/sound/feedback if match; schedules next (2s). Usage: From touchscreen buttons. Insight: Only for quiz; shows correct answer on wrong for learning.
  - **Method: `end_game(self)`** - Transitions to 'score'; sets final score label; focuses name input. Usage: After 3 quizzes. Insight: Prepares VKeyboard.
  - **Method: `submit_score(self, player_name)`** - Validates/trims/uppercases name; creates entry (name, score, ISO timestamp); appends to loaded scores; atomic save; plays sound; transitions to leaderboard. Usage: From Submit button. Insight: Skips empty names; uses `dm` for persistence.
  - **Method: `show_leaderboard(self, player_name=None)`** - Loads/sorts scores (top 15); checks if player in top; sets congrats text; calls `update_leaderboard()`. Usage: Post-submit. Insight: Highlights player in green; sorts descending.
  - **Method: `cleanup(self)`** - Calls `hw.cleanup()`. Usage: On app stop. Insight: Essential for GPIO safety.
  - **Helper Methods**:
    - `go_to_screen(self, screen_name)`: Sets `sm.current`; prints transition. Usage: Universal navigation.
    - `show_instructions(self)`: Sets state='agility'; updates content; transitions. Usage: From welcome.
    - `proceed_from_instructions(self)`: Branches on state (agility->start_game, quiz->start_quiz_section). Usage: From action button.
    - `return_to_welcome(self)`: Resets state; transitions. Usage: From leaderboard 'Play Again'.
  - **Insights**: FSM prevents invalid states (e.g., button press mid-quiz ignored); timings from config; total lines ~260; extensible for more rounds/modes.

### 3. Hardware Abstraction Layer (`app/hardware_io.py`)
- **Class: `HardwareController`** - Abstracts GPIO; uses gpiozero for buttons/LEDs.
  - **Init: `__init__(self)`** - Validates pins; creates `self.buttons = [Button(pin) for pin in BUTTON_PINS]`; `self.leds = [LED(pin, active_high=False) for pin in RELAY_PINS]` (for active-low relays). Usage: Instantiated in GameManager; prints pin counts. Insight: active_high=False inverts signals (on()=LOW for relays); raises ValueError if pins empty.
  - **Method: `set_button_callback(self, callback_func)`** - Assigns lambda-wrapped callback to each button's `when_pressed`. Usage: `self.hw.set_button_callback(self.on_button_press)` in init. Insight: Non-blocking; passes index for multi-button support.
  - **Method: `turn_on_led(self, index)`** - If valid (0-11), `leds[index].on()`. Usage: In agility round start.
  - **Method: `turn_off_led(self, index)`** - If valid, `leds[index].off()`. Usage: Post-press.
  - **Method: `turn_off_all_leds(self)`** - Loops `off()` all. Usage: End sections.
  - **Method: `cleanup(self)`** - Off all; closes buttons/leds; prints. Usage: On exit. Insight: Prevents stuck LEDs.
  - **Insights**: 12 pins each; testable via `test_hardware.py` (cycles LEDs, callbacks); abstracts relay inversion; ~55 lines.

### 4. Data Persistence (`app/data_manager.py`)
- **Class: `DataManager`** - JSON service with atomic writes.
  - **Method: `load_questions(self)`** - Opens/loads `QUESTIONS_FILE`; returns `data['questions']` or []. Usage: In init; handles FileNotFound/JSONDecodeError. Insight: UTF-8; defaults empty for graceful startup.
  - **Method: `load_leaderboard(self)`** - Similar; returns `data['scores']` or []. Usage: For display/submit.
  - **Method: `save_leaderboard(self, scores_data)`** - Dumps to temp file; `os.replace()` atomic; cleans temp on error. Usage: Post-submit. Insight: Prevents corruption mid-write; ~44 lines.
  - **Insights**: Paths from config; sample questions.json has 5 entries (question/options/correct_answer).

### 5. Audio Management (`app/audio_manager.py`)
- **Class: `AudioManager`** - Loads/plays SFX via Kivy SoundLoader.
  - **Init: `__init__(self, sounds_path="assets/sounds/")`** - Maps keys ('start','correct','wrong','submit') to .wav; loads into dict. Usage: In GameManager; warns on failures. Insight: Pre-loads for instant play; ~32 lines.
  - **Method: `play(self, sound_key)`** - If loaded, `sound.play()`; warns else. Usage: E.g., `self.am.play('correct')` on success.
  - **Insights**: ALSA driver fix in main.py; syncs with visuals (e.g., countdown sounds).

### 6. UI Layer (`app/ui/screens.py` & `app/ui/screens.kv`)
- **Screens as Kivy `Screen` subclasses** - Minimal Python logic; KV for layouts/styling.
  - **Class: `WelcomeScreen(Screen)`** - Pass; KV: Logo, "Toque para começar" button -> `app.game_manager.show_instructions()`. Insight: Attract entry.
  - **Class: `InstructionsScreen(Screen)`** - **Method: `update_content(self, title, body, button_text)`** - Sets ids (title_label, body_label, action_button). Usage: From GameManager. KV: Branded dialog box, logo.
  - **Class: `AgilityGameScreen(Screen)`** - Pass; KV: Dark bg, round/score labels, countdown_label (animated), instruction_label (fade-in). Insight: Centered for focus.
  - **Class: `QuizGameScreen(Screen)`** - **Method: `display_question(self, question_data)`** - Sets question_label, option_1-4.text; clears feedback. Usage: From GameManager. KV: White bg, grid buttons -> `check_answer(self.text)`.
  - **Class: `ScoreScreen(Screen)`** - Pass; KV: Score label, name_input (readonly, VKeyboard target), Submit -> `submit_score(name_input.text)`. Insight: Multiline=False, 40-char limit pending.
  - **Class: `LeaderboardScreen(Screen)`** - **Method: `update_leaderboard(self, scores, player_name=None)`** - Clears grid; adds header; loops top 15 (sort desc), highlights player in green. Usage: From show_leaderboard. KV: GridLayout cols=3, 'Play Again' -> return_to_welcome.
  - **Custom: `LeaderboardEntry(BoxLayout)`** - Properties for rank/name/score text. (Unused in current impl; for future rows.)
  - **KV Insights**: Branded styles (colors: primary_blue #004077, green #86BC25; fonts Roboto; rounded buttons); background_graphic opacity 0.15; padding dp(120); fullscreen vertical.

### 7. Configuration (`config.py`)
- **Constants** (no class; direct imports):
  - `BUTTON_PINS = [2,3,4,17,27,22,10,9,11,5,6,13]` - BCM inputs for buttons.
  - `RELAY_PINS = [14,15,18,23,24,25,8,7,12,16,20,21]` - BCM outputs for relays.
  - `INSTRUCTIONS_DURATION=5.0`, `COUNTDOWN_SECONDS=3.0`, `QUIZ_TIME_LIMIT=15.0` - Timings (s).
  - `LEADERBOARD_FILE="data/leaderboard.json"`, `QUESTIONS_FILE="data/questions.json"`.
  - **Insights**: Must match wiring; edit before run; centralizes for easy hardware swaps.

## Setup & Commands
1. **Env Setup**: `python -m venv .venv; source .venv/bin/activate; pip install -r requirements.txt` (kivy, gpiozero, lgpio).
2. **Hardware Test**: `python test_hardware.py` - Cycles LEDs, callbacks on presses; Ctrl+C exit.
3. **Run App**: `python -m app` - Fullscreen kiosk; logs transitions.
4. **Data Init**: Edit `data/questions.json` (array of dicts: question/options/correct_answer); `data/leaderboard.json` auto-populates.
5. **Git**: Standard .gitignore (venv, pyc, .kivy, vscode).
- **Insights**: Test hardware standalone before full run; monitor via prints; for prod, systemd service for autostart.

## Development Insights & Best Practices
- **Performance**: Clock-scheduled events ensure <1ms latency; gpiozero callbacks avoid polling.
- **Extensibility**: Add rounds in GameManager vars; new questions in JSON; mock HAL for sim testing.
- **Debugging**: Prints in callbacks/transitions; handle FileNotFound gracefully.
- **Roadmap Alignment**: Phase 4 pending: Custom VKeyboard (fixed, in-app, 40-char input sync with TextInput); Attract mode (idle LED loop + leaderboard cycle); Audio sync polish.
- **AI Parsing Tips**: Search for method calls (e.g., `Clock.schedule_once`) to trace timing; analyze FSM via state vars; simulate scores with sample data. Total codebase ~1000 LOC; adheres PEP8.