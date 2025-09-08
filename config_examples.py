# Configuration Examples for Interactive Stand Game
# Copy desired configuration to config.py

# ========================================
# EXAMPLE 1: Default Configuration (Current)
# ========================================
"""
# Game Mechanics Configuration
AGILITY_BUTTONS_COUNT = 10          # Number of buttons to press in agility game
AGILITY_MAX_SCORE = 20000          # Maximum score for agility (points deducted by time)
AGILITY_SCORE_PENALTY_PER_MS = 1   # Points deducted per millisecond

QUIZ_ROUNDS_COUNT = 3              # Number of quiz questions per game
QUIZ_POINTS_PER_CORRECT = 500      # Points awarded for each correct answer
"""

# ========================================
# EXAMPLE 2: Quick Game Mode (Shorter sessions)
# ========================================
"""
# Game Mechanics Configuration - QUICK MODE
AGILITY_BUTTONS_COUNT = 5           # Fewer buttons for faster rounds
AGILITY_MAX_SCORE = 10000          # Lower max score
AGILITY_SCORE_PENALTY_PER_MS = 2   # Higher penalty for precision

QUIZ_ROUNDS_COUNT = 2              # Only 2 questions
QUIZ_POINTS_PER_CORRECT = 750      # Higher points per question to balance
"""

# ========================================
# EXAMPLE 3: Challenge Mode (Longer, harder)
# ========================================
"""
# Game Mechanics Configuration - CHALLENGE MODE
AGILITY_BUTTONS_COUNT = 15          # More buttons for endurance
AGILITY_MAX_SCORE = 30000          # Higher max score
AGILITY_SCORE_PENALTY_PER_MS = 0.5 # Lower penalty for longer games

QUIZ_ROUNDS_COUNT = 5              # More questions
QUIZ_POINTS_PER_CORRECT = 400      # Slightly lower per question
"""

# ========================================
# EXAMPLE 4: Kids Mode (Easy and fun)
# ========================================
"""
# Game Mechanics Configuration - KIDS MODE
AGILITY_BUTTONS_COUNT = 3           # Very few buttons
AGILITY_MAX_SCORE = 5000           # Lower max score
AGILITY_SCORE_PENALTY_PER_MS = 0.1 # Very forgiving timing

QUIZ_ROUNDS_COUNT = 2              # Simple quiz
QUIZ_POINTS_PER_CORRECT = 1000     # High reward for participation
"""

# ========================================
# EXAMPLE 5: Tournament Mode (Competitive)
# ========================================
"""
# Game Mechanics Configuration - TOURNAMENT MODE
AGILITY_BUTTONS_COUNT = 12          # Standard competitive count
AGILITY_MAX_SCORE = 25000          # High stakes scoring
AGILITY_SCORE_PENALTY_PER_MS = 1.5 # Precision matters

QUIZ_ROUNDS_COUNT = 4              # Balanced knowledge test
QUIZ_POINTS_PER_CORRECT = 625      # Balanced scoring (2500 max quiz score)
"""

# ========================================
# How to Use These Examples:
# ========================================
"""
1. Choose the configuration that fits your event
2. Copy the desired values to config.py
3. Restart the application
4. The game will automatically use the new settings

Note: Make sure you have enough questions in data/questions.json 
for the QUIZ_ROUNDS_COUNT you choose.
"""