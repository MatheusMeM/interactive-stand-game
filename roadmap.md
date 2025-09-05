
### ** Master Roadmap for the Brand Convention Interactive Game**

Here is the master development roadmap for the project. This document outlines the five key phases of construction. We will tackle each phase sequentially, using this checklist to track our progress. Your mission is to assist in architecting and implementing the tasks within each phase, adhering to the principles outlined in your persona definition.

---

# **Master Roadmap: Interactive Stand Installation**

**Final Objective:** Deliver a robust, stable, and captivating application that runs autonomously on a Raspberry Pi 5, seamlessly integrating a Kivy-based touchscreen UI with 12 physical arcade buttons and LEDs via GPIO.

---

### **Phase 0: Project Foundation & Bootstrap**

**Goal:** Establish the project's backbone, configure the development environment, and ensure basic software components are in place. This phase is about building the foundation before the walls.

- [ ] **Directory Scaffolding:** Create the complete project structure (`app/`, `data/`, `assets/`, `config.py`, etc.) as defined in your persona.
- [ ] **Environment Setup:** Initialize a Python virtual environment (`.venv`) and create a `requirements.txt` file with initial dependencies (`kivy`, `gpiozero`).
- [ ] **Centralized Configuration:** Populate `config.py` with initial constants, including GPIO pin mappings for all 12 buttons and 12 relays, file paths, and core game timings.
- [ ] **Kivy "Hello, World":** Implement the simplest possible Kivy app in `__main__.py` that launches a basic window. This validates the Kivy installation and base application structure.

---

### **Phase 1: Core Services - Hardware & Data Layers**

**Goal:** Abstract and validate communication with the physical hardware (GPIO) and persistent data (JSON). The objective is to have independent, testable modules before implementing game logic.

- [ ] **Hardware Module (`hardware_io.py`):**
    - [ ] Implement a `HardwareController` class to manage all GPIO interactions.
    - [ ] Create high-level, abstract methods: `turn_on_led(index)`, `turn_off_all_leds()`, `get_pressed_button()`.
    - [ ] Configure all 12 button inputs using non-blocking callbacks (`when_pressed`) that will notify the main application.
    - [ ] Develop a standalone test script (`test_hardware.py`) to cycle through all LEDs and print console feedback upon each button press.

- [ ] **Data Module (`data_manager.py`):**
    - [ ] Implement a `DataManager` class.
    - [ ] Create methods to `load_questions()`, `load_leaderboard()`, and `save_leaderboard(data)`.
    - [ ] Implement atomic write logic for `save_leaderboard` to prevent JSON file corruption in case of a crash.

---

### **Phase 2: UI/UX & State Machine - The Application Skeleton**

**Goal:** Construct the UI navigation framework and the central logic engine (FSM) that controls the application flow. At this stage, screens will be placeholders, but navigation between them will be functional.

- [ ] **Kivy ScreenManager:** Configure the main `ScreenManager` in the Kivy app to handle all distinct game screens.
- [ ] **Screen Placeholders:** Create the Python classes and basic `.kv` layout files for all primary screens: `WelcomeScreen`, `InstructionsScreen`, `AgilityGameScreen`, `QuizGameScreen`, `ScoreScreen`, and `LeaderboardScreen`.
- [ ] **Finite State Machine (`game_manager.py`):**
    - [ ] Implement the `GameManager` class, which will serve as the application's central brain.
    - [ ] Define all game states (e.g., `IDLE`, `INSTRUCTIONS`, `PLAYING_AGILITY`, `SHOWING_LEADERBOARD`).
    - [ ] Create methods to transition between states (e.g., `start_game()`, `end_round()`), which will instruct the `ScreenManager` to change the visible screen.

---

### **Phase 3: Game Logic Implementation - The Heart of the Experience**

**Goal:** Infuse the placeholder screens with life by implementing the core agility game mechanics, the quiz system, and the scoring logic.

- [ ] **Agility Game Logic:**
    - [ ] Implement the countdown timer on the `AgilityGameScreen`.
    - [ ] In the `GameManager`, develop the logic to randomly select an LED, activate it via the `HardwareController`, and start a high-precision timer.
    - [ ] Integrate the button press callback from the `HardwareController` to stop the timer, calculate the response time in milliseconds, and update the player's score.

- [ ] **Quiz Game Logic:**
    - [ ] On the `QuizGameScreen`, use the `DataManager` to fetch a random question and populate the UI with the question text and four answer options.
    - [ ] Implement the logic to detect a touch event on an answer, check if it is correct, provide immediate visual feedback (green for correct, red for incorrect), and update the score.

- [ ] **Scoring & Leaderboard Logic:**
    - [ ] On the `ScoreScreen`, implement the Kivy virtual keyboard for player name input.
    - [ ] Upon submission, use the `DataManager` to save the final score, player name, and timestamp to `leaderboard.json`.
    - [ ] On the `LeaderboardScreen`, fetch the top 15 scores, sort them, and display them. Implement the logic to highlight the current player's entry and show a "Congratulations!" message if they made the leaderboard.

---

### **Phase 4: Integration, Polish & Feedback - The Soul of the Game**

**Goal:** Weave all modules together, refine the user experience with audiovisual feedback, and ensure the full game loop is seamless, engaging, and polished.

- [ ] **Full Loop Integration:** Connect the game states to create the final flow: 2 rounds of agility and 2 rounds of quiz, with scoring accumulated correctly.
- [ ] **Sensory Feedback:** Integrate sound effects for key events: button press, correct/incorrect answers, round start, and game over.
- [ ] **UI Polish:** Implement smooth screen transitions in the `ScreenManager`. Add subtle, non-blocking animations for the countdown and score updates to make the UI feel more dynamic.
- [ ] **Attract Mode:** Implement the idle state loop on the `WelcomeScreen`. This should alternate between showing the "Touch to Start" message and the global leaderboard, accompanied by an engaging light pattern on the physical buttons to attract passersby.

---

### **Phase 5: Deployment & Stress Testing - Stage Ready**

**Goal:** Prepare the application for robust, unattended operation in the live convention environment.

- [ ] **Autostart Service:** Create a `systemd` service file to launch the Python Kivy application automatically on boot in the production Raspberry Pi environment.
- [ ] **Kiosk Mode Configuration:** Configure the Raspberry Pi OS to run the application in full-screen (kiosk) mode, hiding the desktop environment and mouse cursor.
- [ ] **Stress Testing:** Run the application in a continuous, automated loop for an extended period (12+ hours) to identify and fix potential memory leaks or performance degradation over time.
- [ ] **Operational Runbook:** Create a simple, one-page guide for the on-site staff covering system startup, shutdown, and basic troubleshooting steps (e.g., "How to restart the application").