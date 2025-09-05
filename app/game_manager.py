import random
import time
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager
from app.hardware_io import HardwareController
from app.data_manager import DataManager
from app.audio_manager import AudioManager
import datetime

class GameManager:
    def __init__(self, screen_manager: ScreenManager):
        self.sm = screen_manager
        self.hw = HardwareController()
        self.dm = DataManager()
        self.am = AudioManager()
        self.hw.set_button_callback(self.on_button_press)

        self.all_questions = self.dm.load_questions()
        self.questions_for_round = []

        self.score = 0
        self.total_agility_rounds = 5
        self.current_agility_round = 0
        self.agility_in_progress = False
        self.target_led_index = -1
        self.round_start_time = 0
        
        self.total_quiz_rounds = 3
        self.current_quiz_round = 0
        self.current_question_data = None
        self.quiz_in_progress = False

        print("GameManager initialized with HardwareController and DataManager.")

    def start_game(self):
        """Resets game state and starts the countdown for the agility game."""
        self.am.play('start')
        self.score = 0
        self.current_agility_round = 0
        self.current_quiz_round = 0
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
                return False
        
        Clock.schedule_interval(update_countdown, 1)

    def start_agility_round(self, dt=None):
        """Starts a single round of the agility game."""
        # --- THIS IS THE NEW LOGIC ---
        # First, check if the agility section is over.
        if self.current_agility_round >= self.total_agility_rounds:
            self.end_agility_section()
            return
        # --- END OF NEW LOGIC ---

        self.current_agility_round += 1

        screen = self.sm.get_screen('agility_game')
        screen.ids.round_label.text = f'Round: {self.current_agility_round} / {self.total_agility_rounds}'
        screen.ids.score_label.text = f'Score: {self.score}'
        screen.ids.countdown_label.text = ''

        self.target_led_index = random.randint(0, len(self.hw.leds) - 1)
        self.hw.turn_on_led(self.target_led_index)
        self.round_start_time = time.perf_counter()
        self.agility_in_progress = True

    def on_button_press(self, pressed_index):
        """Callback for PHYSICAL button presses (Agility Game ONLY)."""
        if not self.agility_in_progress: return
        self.agility_in_progress = False
        self.hw.turn_off_led(self.target_led_index)
        
        if pressed_index == self.target_led_index:
            reaction_time = time.perf_counter() - self.round_start_time
            points = max(0, 1000 - int(reaction_time * 1000))
            self.score += points
            self.am.play('correct')
            print(f"Correct! Time: {reaction_time:.3f}s, Score: +{points}")
        else:
            self.am.play('wrong')
            print(f"Wrong button! Expected {self.target_led_index}, got {pressed_index}.")

        # --- THIS IS THE CRITICAL CHANGE ---
        # Schedule the next round to start after a brief delay.
        # The start_agility_round function itself will now handle the logic of when to stop.
        Clock.schedule_once(self.start_agility_round, 0.5)

    def end_agility_section(self):
        """Called ONCE after the last agility round. Transitions to the quiz."""
        print("Agility section finished. Starting Quiz section.")
        self.hw.turn_off_all_leds()

        # Ensure we have enough questions to sample from.
        if len(self.all_questions) < self.total_quiz_rounds:
             print(f"Error: Not enough questions in questions.json. Found {len(self.all_questions)}, need {self.total_quiz_rounds}.")
             # As a fallback, just end the game.
             self.end_game()
             return

        self.go_to_screen('quiz_game')
        self.questions_for_round = random.sample(self.all_questions, self.total_quiz_rounds)
        Clock.schedule_once(self.start_quiz_round, 1.0)
        
    def start_quiz_round(self, dt=None):
        """Starts a single round of the quiz game."""
        if self.current_quiz_round >= len(self.questions_for_round):
            self.end_game()
            return

        self.current_question_data = self.questions_for_round[self.current_quiz_round]
        screen = self.sm.get_screen('quiz_game')
        screen.display_question(self.current_question_data)
        self.quiz_in_progress = True
        self.current_quiz_round += 1

    def check_answer(self, selected_answer: str):
        """Callback for TOUCHSCREEN answer buttons (Quiz Game ONLY)."""
        if not self.quiz_in_progress:
            return
        self.quiz_in_progress = False

        screen = self.sm.get_screen('quiz_game')
        correct_answer = self.current_question_data['correct_answer']

        if selected_answer == correct_answer:
            self.score += 500 # Fixed points for a correct quiz answer
            self.am.play('correct')
            screen.ids.feedback_label.text = 'Correct!'
            print("Quiz answer: Correct!")
        else:
            self.am.play('wrong')
            screen.ids.feedback_label.text = f'Wrong! The correct answer was:\n{correct_answer}'
            print("Quiz answer: Incorrect!")

        Clock.schedule_once(self.start_quiz_round, 2.0) # Wait 2 seconds before next question

    def end_game(self):
        """Called after the last quiz round. Transitions to the Score screen."""
        print(f"Game over! Final Score: {self.score}")
        self.go_to_screen('score')
        screen = self.sm.get_screen('score')
        screen.ids.final_score_label.text = f'Your Final Score: {self.score}'
        screen.ids.name_input.text = '' # Clear input field

    def validate_name_input(self, text_input):
        """Restricts name input to 3 characters."""
        if len(text_input.text) > 3:
            text_input.text = text_input.text[:3]
            # Move cursor to end
            text_input.cursor = (3, 0)

    def submit_score(self, player_name):
        """Validates, saves, and displays the player's score."""
        if len(player_name) != 3:
            print("Name must be exactly 3 characters")
            # In a real app, you'd show an error message on screen
            return
        
        # Add timestamp and save
        score_entry = {
            'name': player_name,
            'score': self.score,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        # Load existing scores, add new one, and save
        all_scores = self.dm.load_leaderboard()
        all_scores.append(score_entry)
        self.am.play('submit')
        self.dm.save_leaderboard(all_scores)
        
        # Go to leaderboard
        self.go_to_screen('leaderboard')
        self.show_leaderboard(player_name)

    def show_leaderboard(self, player_name=None):
        """Loads and displays the leaderboard."""
        scores = self.dm.load_leaderboard()
        screen = self.sm.get_screen('leaderboard')
        
        # Show a congratulations message if the player is in the top 15
        top_scores = sorted(scores, key=lambda x: x['score'], reverse=True)[:15]
        is_top_player = any(entry.get('name') == player_name for entry in top_scores)
        
        if is_top_player:
            screen.ids.congrats_label.text = f"Congratulations {player_name}! You're in the Hall of Fame!"
        else:
            screen.ids.congrats_label.text = ""
        
        screen.update_leaderboard(scores, player_name)

    def cleanup(self):
        """Should be called when the app closes."""
        self.hw.cleanup()

    # --- Screen Transition Methods ---
    def go_to_screen(self, screen_name):
        """A generic method to switch screens."""
        print(f"Transitioning to {screen_name} screen.")
        self.sm.current = screen_name

    def show_instructions(self):
        """Transitions the view to the instructions screen."""
        self.go_to_screen('instructions')

    def return_to_welcome(self):
        """Returns to the welcome screen and resets the game state."""
        self.score = 0
        self.current_agility_round = 0
        self.current_quiz_round = 0
        self.go_to_screen('welcome')