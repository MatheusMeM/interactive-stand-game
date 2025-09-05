from kivy.uix.screenmanager import ScreenManager

class GameManager:
    """
    The core Finite State Machine (FSM). Manages application state and screen transitions.
    """
    def __init__(self, screen_manager: ScreenManager):
        self.sm = screen_manager
        self.current_state = 'WELCOME'
        print("GameManager initialized, starting at WELCOME state.")

    def go_to_screen(self, screen_name):
        """A generic method to switch screens."""
        print(f"Transitioning to {screen_name} screen.")
        self.sm.current = screen_name

    # --- State Transition Methods ---
    def show_instructions(self):
        self.go_to_screen('instructions')

    def start_game(self):
        # This will later contain logic to start the first round
        self.go_to_screen('agility_game')

    def show_leaderboard(self):
        self.go_to_screen('leaderboard')
        
    def return_to_welcome(self):
        self.go_to_screen('welcome')