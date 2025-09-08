# Master Roadmap: Interactive Stand Installation

### Phase 0: Project Foundation & Bootstrap
- [x] **Directory Scaffolding:** Create the complete project structure.
- [x] **Environment Setup:** Initialize a Python virtual environment and `requirements.txt`.
- [x] **Centralized Configuration:** Populate `config.py` with initial constants.
- [x] **Kivy "Hello, World":** Implement the simplest possible Kivy app.

### Phase 1: Core Services - Hardware & Data Layers
- [x] **Hardware Module (`hardware_io.py`):**
    - [x] Implement a `HardwareController` class.
    - [x] Create high-level, abstract methods.
    - [x] Configure all button inputs using non-blocking callbacks.
    - [x] Develop a standalone test script.
- [x] **Data Module (`data_manager.py`):**
    - [x] Implement a `DataManager` class.
    - [x] Create methods to `load_questions()`, `load_leaderboard()`, and `save_leaderboard(data)`.
    - [x] Implement atomic write logic.

### Phase 2: UI/UX & State Machine - The Application Skeleton
- [x] **Kivy ScreenManager:** Configure the main `ScreenManager`.
- [x] **Screen Placeholders:** Create the Python classes and basic `.kv` layout files.
- [x] **Finite State Machine (`game_manager.py`):** Implement the `GameManager` class.

### Phase 3: Game Logic Implementation - The Heart of the Experience
- [x] **Agility Game Logic:**
    - [x] Implement the countdown on the `AgilityGameScreen`.
    - [x] Develop the logic for random LED activation and high-precision timing.
    - [x] Integrate the button press callback to calculate score and advance rounds.
- [x] **Quiz Game Logic:**
    - [x] On the `QuizGameScreen`, use the `DataManager` to fetch and display a question.
    - [x] Implement the logic to check user answers and update the score.
- [x] **Scoring & Leaderboard Logic:**
    - [x] On the `ScoreScreen`, implement the Kivy virtual keyboard.
    - [x] Save the final score and player name using the `DataManager`.
    - [x] Display and highlight the player's score on the `LeaderboardScreen`.

### Phase 4: UI/UX Overhaul & Polishing
- [x] **Foundational UI Setup:**
    - [x] Configure the application to run in **Fullscreen Mode**.
    - [x] Set and lock the screen orientation to **Vertical**.
- [ ] **Brand Integration & UI Redesign:**
    - [x] Integrate brand assets (logo, graphics) into the `assets/images` folder.
    - [ ] Redesign all screens in `screens.kv` using the IBP brand guide (colors, shapes, and recommended fonts).
    - [ ] Replace the standard `TextInput` on the `ScoreScreen` with a **built-in Kivy Virtual Keyboard**, that is fixed on the screen and cannot move around, and its not the default system keyboard, it must be made in game, also i want to be able to input with or standart textinput, so a keyboard laso inputs text into the field. Ps. Field can be up to 40 chars total (including spaces)
- [ ] **Experience Refinement:**
    - [x] **Sensory Feedback:** Integrate sound effects for key events.
    - [ ] **Audio Adjust:** Refine and polish audio trigger events nad sync with text for countdown screen.
    - [ ] **UI Polish:** Implement smooth, non-disruptive screen transitions (e.g., `FadeTransition`).
    - [ ] **Attract Mode:** Implement an idle state loop on the `WelcomeScreen` that alternates with the Leaderboard and triggers an engaging LED light pattern.
- [ ] **Final Loop Integration & Testing:**
    - [ ] Conduct a full review of the game loop, testing for consistency and minor bugs.

### Phase 5: Deployment & Stress Testing - Stage Ready
- [ ] **Autostart Service:** Create a `systemd` service file.
- [ ] **Kiosk Mode Configuration:** Ensure the OS is locked down for public use.
- [ ] **Stress Testing:** Run the application for an extended period to check for stability.
- [ ] **Operational Runbook:** Create a simple guide for on-site staff.