#!/usr/bin/env python3
"""
Test script to validate game mechanics configuration
Tests different config values without running the full GUI
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config_import():
    """Test that config values can be imported correctly"""
    try:
        from config import (AGILITY_BUTTONS_COUNT, AGILITY_MAX_SCORE, AGILITY_SCORE_PENALTY_PER_MS,
                           QUIZ_ROUNDS_COUNT, QUIZ_POINTS_PER_CORRECT)
        
        print("✅ Config import successful")
        print(f"   Agility Buttons: {AGILITY_BUTTONS_COUNT}")
        print(f"   Agility Max Score: {AGILITY_MAX_SCORE}")
        print(f"   Agility Penalty/ms: {AGILITY_SCORE_PENALTY_PER_MS}")
        print(f"   Quiz Rounds: {QUIZ_ROUNDS_COUNT}")
        print(f"   Quiz Points/Correct: {QUIZ_POINTS_PER_CORRECT}")
        return True
    except ImportError as e:
        print(f"❌ Config import failed: {e}")
        return False

def test_agility_scoring():
    """Test agility scoring calculation with different times"""
    from config import AGILITY_MAX_SCORE, AGILITY_SCORE_PENALTY_PER_MS
    
    print("\n🎯 Testing Agility Scoring:")
    test_times = [1.0, 2.5, 5.0, 10.0, 15.0, 20.0]
    
    for time_seconds in test_times:
        time_ms = int(time_seconds * 1000)
        score = max(0, AGILITY_MAX_SCORE - (time_ms * AGILITY_SCORE_PENALTY_PER_MS))
        print(f"   {time_seconds:4.1f}s ({time_ms:5d}ms) → {score:6d} points")
    
    # Test edge cases
    max_time = AGILITY_MAX_SCORE / AGILITY_SCORE_PENALTY_PER_MS / 1000
    print(f"   Max time for 0 points: {max_time:.1f}s")

def test_quiz_scoring():
    """Test quiz scoring calculation"""
    from config import QUIZ_ROUNDS_COUNT, QUIZ_POINTS_PER_CORRECT
    
    print(f"\n📚 Testing Quiz Scoring:")
    print(f"   Questions per game: {QUIZ_ROUNDS_COUNT}")
    print(f"   Points per correct: {QUIZ_POINTS_PER_CORRECT}")
    
    max_quiz_score = QUIZ_ROUNDS_COUNT * QUIZ_POINTS_PER_CORRECT
    print(f"   Maximum quiz score: {max_quiz_score}")
    
    for correct in range(QUIZ_ROUNDS_COUNT + 1):
        score = correct * QUIZ_POINTS_PER_CORRECT
        percentage = (correct / QUIZ_ROUNDS_COUNT) * 100
        print(f"   {correct}/{QUIZ_ROUNDS_COUNT} correct ({percentage:5.1f}%) → {score:4d} points")

def test_total_scoring():
    """Test combined scoring scenarios"""
    from config import (AGILITY_MAX_SCORE, AGILITY_SCORE_PENALTY_PER_MS,
                       QUIZ_ROUNDS_COUNT, QUIZ_POINTS_PER_CORRECT)
    
    print(f"\n🏆 Testing Combined Scoring Scenarios:")
    
    # Perfect game
    perfect_agility = AGILITY_MAX_SCORE
    perfect_quiz = QUIZ_ROUNDS_COUNT * QUIZ_POINTS_PER_CORRECT
    perfect_total = perfect_agility + perfect_quiz
    print(f"   Perfect game: {perfect_total} points (Agility: {perfect_agility}, Quiz: {perfect_quiz})")
    
    # Average game (5s agility, 2/3 quiz correct)
    avg_agility_time = 5.0
    avg_agility_score = max(0, AGILITY_MAX_SCORE - int(avg_agility_time * 1000 * AGILITY_SCORE_PENALTY_PER_MS))
    avg_quiz_correct = min(2, QUIZ_ROUNDS_COUNT)
    avg_quiz_score = avg_quiz_correct * QUIZ_POINTS_PER_CORRECT
    avg_total = avg_agility_score + avg_quiz_score
    print(f"   Average game: {avg_total} points (Agility: {avg_agility_score}, Quiz: {avg_quiz_score})")
    
    # Poor game (15s agility, 0 quiz correct)
    poor_agility_time = 15.0
    poor_agility_score = max(0, AGILITY_MAX_SCORE - int(poor_agility_time * 1000 * AGILITY_SCORE_PENALTY_PER_MS))
    poor_quiz_score = 0
    poor_total = poor_agility_score + poor_quiz_score
    print(f"   Poor game: {poor_total} points (Agility: {poor_agility_score}, Quiz: {poor_quiz_score})")

def test_data_requirements():
    """Test if data files meet the configuration requirements"""
    from config import QUIZ_ROUNDS_COUNT
    from app.data_manager import DataManager
    
    print(f"\n📁 Testing Data Requirements:")
    
    dm = DataManager()
    questions = dm.load_questions()
    
    print(f"   Questions available: {len(questions)}")
    print(f"   Questions needed: {QUIZ_ROUNDS_COUNT}")
    
    if len(questions) >= QUIZ_ROUNDS_COUNT:
        print("   ✅ Sufficient questions available")
    else:
        print("   ❌ Not enough questions! Add more to data/questions.json")
        return False
    
    return True

def main():
    """Run all configuration tests"""
    print("🔧 Testing Game Mechanics Configuration")
    print("=" * 50)
    
    tests = [
        test_config_import,
        test_agility_scoring,
        test_quiz_scoring,
        test_total_scoring,
        test_data_requirements
    ]
    
    all_passed = True
    for test in tests:
        try:
            result = test()
            if result is False:
                all_passed = False
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with error: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All configuration tests passed!")
        print("🚀 Game is ready to run with current config values")
    else:
        print("❌ Some tests failed. Check configuration and data files.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())