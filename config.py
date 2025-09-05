# Central Configuration File

# 1. GPIO Pin Mapping (BCM numbering)
# These must be filled with the actual BCM pin numbers you will use.
# Example: BUTTON_PINS = [4, 17, 27, ...]
BUTTON_PINS = []  # 12 pins for arcade buttons
RELAY_PINS = []   # 12 pins for relay channels controlling LEDs

# 2. Game Timings (in seconds)
INSTRUCTIONS_DURATION = 5.0
COUNTDOWN_SECONDS = 3.0
QUIZ_TIME_LIMIT = 15.0

# 3. File Paths
LEADERBOARD_FILE = "data/leaderboard.json"
QUESTIONS_FILE = "data/questions.json"