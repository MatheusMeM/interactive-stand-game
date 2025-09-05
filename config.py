# Central Configuration File

# 1. GPIO Pin Mapping (BCM numbering)
# These must be filled with the actual BCM pin numbers you will use.
# Example: BUTTON_PINS = [4, 17, 27, ...]
BUTTON_PINS = [2, 3, 4, 17, 27, 22, 10, 9, 11, 5, 6, 13]  # 12 pins for arcade buttons
RELAY_PINS = [14, 15, 18, 23, 24, 25, 8, 7, 12, 16, 20, 21]   # 12 pins for relay channels controlling LEDs

# 2. Game Timings (in seconds)
INSTRUCTIONS_DURATION = 5.0
COUNTDOWN_SECONDS = 3.0
QUIZ_TIME_LIMIT = 15.0

# 3. File Paths
LEADERBOARD_FILE = "data/leaderboard.json"
QUESTIONS_FILE = "data/questions.json"