# Interactive Stand Game - RPi5 & Kivy

A high-response interactive game for a brand convention, built with Python/Kivy on a Raspberry Pi 5, integrating a touchscreen UI with 12 physical arcade buttons and LEDs.

## 1. Core Premise

The application is a gamified experience designed for high-traffic environments. It consists of two alternating mini-games controlled by a central state machine:
*   **Agility Game:** Measures player reaction time in milliseconds. A random LED lights up, and the player must press the corresponding physical button as quickly as possible.
*   **Quiz Game:** Tests player knowledge about the brand. Questions are displayed on a touchscreen, and answers are selected via touch.

The final score is a combination of performance in both games. A local leaderboard, stored in a JSON file, tracks the top 15 players.

## 2. Technical Architecture

The system is designed with a strict **Separation of Concerns (SoC)** principle, orchestrated by a Finite State Machine.

*   **Frontend / UI (`Kivy`):** The entire graphical user interface is built using the Kivy framework for its GPU acceleration and native multi-touch support. A `ScreenManager` handles all screen transitions, acting as the view layer for our state machine.
*   **Backend / Game Logic (`Python 3`):** The core logic resides in a central **Finite State Machine (FSM)**, the `GameManager`. This module orchestrates the entire player journey, from the attract screen to the leaderboard, without containing any UI or direct hardware code.
*   **Hardware Abstraction Layer (HAL) (`gpiozero`):** All interactions with the Raspberry Pi's GPIO pins are abstracted into a single `HardwareController` module. This layer provides a simple API (e.g., `turn_on_led(5)`) to the `GameManager`. It uses the `gpiozero` library's non-blocking, callback-based features (`when_pressed`) to ensure the main application thread is never blocked.
*   **Data Persistence (`JSON`):** All persistent data, including quiz questions and the leaderboard, is stored in simple `.json` files. A `DataManager` module handles all read/write operations, utilizing an atomic write strategy to prevent data corruption.

## 3. Project Structure

```
.
├── app/
│   ├── __main__.py           # Main application entry point. Initializes Kivy App and GameManager.
│   ├── game_manager.py       # The core Finite State Machine (FSM). Controls game flow.
│   ├── hardware_io.py        # Hardware Abstraction Layer (HAL). Manages all GPIO.
│   ├── data_manager.py       # Service for reading/writing JSON data.
│   └── ui/                   # Kivy screen modules (.py) and layouts (.kv).
│       ├── screens.py        # Python classes for all Kivy Screens.
│       └── screens.kv        # KV language definitions for UI layouts.
├── data/
│   ├── leaderboard.json      # Stores player scores and names.
│   └── questions.json        # The question bank for the quiz game.
├── assets/
│   ├── images/               # UI images.
│   └── sounds/               # Sound effects.
├── config.py                 # Central configuration: GPIO pins, timings, file paths.
├── requirements.txt          # Python project dependencies.
└── README.md                 # This file.
```

## 4. Setup & Execution

1.  **Clone Repository:**
    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```
2.  **Create & Activate Virtual Environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run Application:**
    ```bash
    python -m app
    ```

## 5. Core Module Responsibilities

| Module                  | File(s)                   | Primary Responsibility                                                                |
| ----------------------- | ------------------------- | ------------------------------------------------------------------------------------- |
| **App Entry Point**     | `app/__main__.py`         | Initializes the main Kivy `App` class and the `GameManager`. Runs the application.    |
| **Game State Machine**  | `app/game_manager.py`     | The application's brain. Manages states, score, timers, and coordinates all modules.    |
| **Hardware Controller** | `app/hardware_io.py`      | Single point of contact for all physical I/O. Abstracts GPIO logic. Non-blocking.     |
| **Data Controller**     | `app/data_manager.py`     | Handles all file I/O operations for `leaderboard.json` and `questions.json`.          |
| **UI Views**            | `app/ui/`                 | Contains all Kivy `Screen` classes and their associated `.kv` layout definitions.     |
| **Configuration**       | `config.py`               | Single source of truth for all constants (GPIO pins, timings, file paths, etc.).      |

## 6. Configuration (`config.py`)

This file is critical. **NO** magic numbers or hardcoded paths should exist outside of this file. It must define:
*   **GPIO Pin Mapping:** Python lists or dictionaries mapping the 12 buttons and 12 relay-controlled LEDs to their specific BCM pin numbers.
*   **Game Timings:** Durations for countdowns, quiz question time limits, and screen transition delays.
*   **File Paths:** Absolute or relative paths to the `data` and `assets` directories.

## 7. Core Development Principles

*   **FSM is Law:** All application flow is explicitly controlled by state transitions within the `GameManager`.
*   **Strict SoC:** The `ui` layer only displays data. The `game_manager` only processes logic. The `hardware_io` only talks to pins.
*   **Never Block:** No `time.sleep()`. All timed events must be scheduled with `kivy.clock.Clock`. All hardware input is handled via asynchronous callbacks.
*   **Config-Driven:** The application must be fully configurable via `config.py` without changing logic files.