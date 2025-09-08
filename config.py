# Central Configuration File

# 1. GPIO Pin Mapping (BCM numbering)
# These must be filled with the actual BCM pin numbers you will use.
# Example: BUTTON_PINS = [4, 17, 27, ...]

BUTTON_PINS = [13, 6, 5, 2, 3, 4, 11, 9, 10, 17, 27, 22]
RELAY_PINS  = [7, 8, 21, 25, 24, 23, 20, 16, 12, 18, 15, 14]


# 2. Game Mechanics Configuration
# Agility Game Settings
AGILITY_BUTTONS_COUNT = 8          # Number of buttons to press in agility game
AGILITY_MAX_SCORE = 20000          # Maximum score for agility (points deducted by time)
AGILITY_SCORE_PENALTY_PER_MS = 1   # Points deducted per millisecond

# Quiz Game Settings
QUIZ_ROUNDS_COUNT = 4              # Number of quiz questions per game
QUIZ_POINTS_PER_CORRECT = 500      # Points awarded for each correct answer

# 3. Game Timings (in seconds)
INSTRUCTIONS_DURATION = 5.0
COUNTDOWN_SECONDS = 3.0
QUIZ_TIME_LIMIT = 15.0

# 4. File Paths
LEADERBOARD_FILE = "data/leaderboard.json"
QUESTIONS_FILE = "data/questions.json"
