import random
import time
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager
from app.hardware_io import HardwareController

class GameManager:
    def __init__(self, screen_manager: ScreenManager):
        self.sm = screen_manager
        self.hw = HardwareController()
        self.hw.set_button_callback(self.on_button_press)

        # Game State
        self.score = 0
        self.total_rounds = 5
        self.current_round = 0
        self.game_in_progress = False
        self.target_led_index = -1
        self.round_start_time = 0

        print("GameManager initialized with HardwareController.")

    def start_game(self):
        """Resets game state and starts the countdown."""
        self.score = 0
        self.current_round = 0
        self.go_to_screen('agility_game')
        self.start_countdown()

    def start_countdown(self, dt=None):
        """Handles the 3, 2, 1 countdown on the screen."""
        screen = self.sm.get_screen('agility_game')
        countdown_val = 3
        
        def update_countdown(dt):
            nonlocal countdown_val
            if countdown_val > 0:
                screen.ids.countdown_label.text = str(countdown_val)
                countdown_val -= 1
            else:
                screen.ids.countdown_label.text = 'GO!'
                Clock.schedule_once(self.start_agility_round, 0.5)
                return False # Stop the scheduled interval
        
        Clock.schedule_interval(update_countdown, 1)

    def start_agility_round(self, dt=None):
        """Starts a single round of the agility game."""
        self.current_round += 1
        if self.current_round > self.total_rounds:
            self.end_game()
            return

        screen = self.sm.get_screen('agility_game')
        screen.ids.round_label.text = f'Round: {self.current_round} / {self.total_rounds}'
        screen.ids.score_label.text = f'Score: {self.score}'
        screen.ids.countdown_label.text = '' # Clear countdown text

        self.target_led_index = random.randint(0, len(self.hw.leds) - 1)
        self.hw.turn_on_led(self.target_led_index)
        self.round_start_time = time.perf_counter() # High precision timer
        self.game_in_progress = True

    def on_button_press(self, pressed_index):
        """Callback executed by HardwareController when any button is pressed."""
        if not self.game_in_progress:
            return

        self.game_in_progress = False # Prevent multiple presses for the same round
        self.hw.turn_off_led(self.target_led_index)
        
        if pressed_index == self.target_led_index:
            reaction_time = time.perf_counter() - self.round_start_time
            # Scoring: less time = more points. Capped at 1000.
            points = max(0, 1000 - int(reaction_time * 1000))
            self.score += points
            print(f"Correct! Time: {reaction_time:.3f}s, Score: +{points}")
        else:
            print(f"Wrong button! Expected {self.target_led_index}, got {pressed_index}.")

        # Start the next round after a short delay
        Clock.schedule_once(self.start_agility_round, 0.5)

    def end_game(self):
        """Called after the last round."""
        print(f"Game over! Final Score: {self.score}")
        # For now, just go back to the welcome screen. Later this will go to the score screen.
        self.return_to_welcome()

    def cleanup(self):
        """Should be called when the app closes."""
        self.hw.cleanup()

    # --- Screen Transition Methods ---
    def go_to_screen(self, screen_name):
        """A generic method to switch screens."""
        print(f"Transitioning to {screen_name} screen.")
        self.sm.current = screen_name

    # --- THIS IS THE NEW METHOD ---
    def show_instructions(self):
        """Transitions the view to the instructions screen."""
        self.go_to_screen('instructions')
    # --- END OF NEW METHOD ---

    def return_to_welcome(self):
        self.go_to_screen('welcome')