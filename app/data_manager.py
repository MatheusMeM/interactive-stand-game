import json
import os
from config import LEADERBOARD_FILE, QUESTIONS_FILE

class DataManager:
    """Handles all data persistence for the application (reading/writing JSON)."""

    def load_questions(self):
        """Loads the quiz questions from the JSON file."""
        try:
            with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("questions", [])
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Warning: Could not load or parse {QUESTIONS_FILE}. Returning empty list.")
            return []

    def load_leaderboard(self):
        """Loads the leaderboard data from the JSON file."""
        try:
            with open(LEADERBOARD_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("scores", [])
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Warning: Could not load or parse {LEADERBOARD_FILE}. Returning empty list.")
            return []

    def save_leaderboard(self, scores_data):
        """
        Saves the leaderboard data to its JSON file using an atomic write operation
        to prevent data corruption.
        """
        temp_file = LEADERBOARD_FILE + ".tmp"
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump({"scores": scores_data}, f, indent=4)
            
            # Atomically rename the temp file to the final file
            os.replace(temp_file, LEADERBOARD_FILE)
        except Exception as e:
            print(f"Error saving leaderboard: {e}")
            # If a temp file was created but rename failed, clean it up
            if os.path.exists(temp_file):
                os.remove(temp_file)