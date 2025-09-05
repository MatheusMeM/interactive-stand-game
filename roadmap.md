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
- [ ] **Scoring & Leaderboard Logic:**
    - [ ] On the `ScoreScreen`, implement the Kivy virtual keyboard.
    - [ ] Save the final score and player name using the `DataManager`.
    - [ ] Display and highlight the player's score on the `LeaderboardScreen`.

### Phase 4: Integration, Polish & Feedback - The Soul of the Game
- [ ] **Full Loop Integration:** Connect game states to create the final flow.
- [ ] **Sensory Feedback:** Integrate sound effects for key events.
- [ ] **UI Polish:** Implement smooth screen transitions and animations.
- [ ] **Attract Mode:** Implement the idle state loop on the `WelcomeScreen`.

### Phase 5: Deployment & Stress Testing - Stage Ready
- [ ] **Autostart Service:** Create a `systemd` service file.
- [ ] **Kiosk Mode Configuration:** Configure the OS for full-screen mode.
- [ ] **Stress Testing:** Run the application for an extended period.
- [ ] **Operational Runbook:** Create a simple guide for on-site staff.