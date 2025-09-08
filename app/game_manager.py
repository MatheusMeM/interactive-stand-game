import random
import time
from kivy.clock import Clock
from kivy.animation import Animation
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
        self.instruction_state = None # <-- NEW state variable

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
        """Handles the 3, 2, 1 countdown and triggers GO animation."""
        screen = self.sm.get_screen('agility_game')
        screen.ids.countdown_label.text = 'Prepare-se!' # Set initial text in PT-BR
        screen.ids.countdown_label.scale = 1.0 # Reset scale
        screen.ids.instruction_label.opacity = 0 # Ensure instruction is hidden
        countdown_val = 3
        
        def update_countdown(dt):
            nonlocal countdown_val
            if countdown_val > 0:
                screen.ids.countdown_label.text = str(countdown_val)
                self.am.play('start') # Play sound on each count
                countdown_val -= 1
            else:
                screen.ids.countdown_label.text = 'VAI!'
                self.am.play('submit') # Use a different sound for GO

                # --- Punch-out Animation for "GO!" ---
                anim = (Animation(scale=1.5, d=0.1) +
                        Animation(scale=1.0, d=0.2, t='out_back'))
                anim.start(screen.ids.countdown_label)

                # --- Fade-in the reinforcing instruction ---
                screen.ids.instruction_label.text = 'APERTE O BOTÃO ACESO!'
                Animation(opacity=1, d=0.3).start(screen.ids.instruction_label)

                Clock.schedule_once(self.start_agility_round, 0.5)
                return False # Stop the scheduled interval
        
        # Start countdown after a brief pause
        Clock.schedule_once(lambda dt: Clock.schedule_interval(update_countdown, 1), 1.0)

    def start_agility_round(self, dt=None):
        """Starts a single round of the agility game."""
        if self.current_agility_round >= self.total_agility_rounds:
            self.end_agility_section()
            return

        self.current_agility_round += 1

        screen = self.sm.get_screen('agility_game')
        screen.ids.round_label.text = f'Rodada: {self.current_agility_round} / {self.total_agility_rounds}'
        screen.ids.score_label.text = f'Pontos: {self.score}'
        
        # --- Hide the "GO!" text and instruction for the round ---
        screen.ids.countdown_label.text = ''
        screen.ids.instruction_label.opacity = 0

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
        """Called after agility. Prepares and shows instructions for the QUIZ game."""
        print("Agility section finished. Showing Quiz instructions.")
        self.hw.turn_off_all_leds()
        self.instruction_state = 'quiz'
        screen = self.sm.get_screen('instructions')
        screen.update_content(
            title='[b]Como Jogar: Quiz[/b]',
            body='Agora, teste seu conhecimento! Responda as perguntas na tela para somar mais pontos.',
            button_text='COMEÇAR QUIZ'
        )
        self.go_to_screen('instructions')
    
    def start_quiz_section(self):
        """Prepares the quiz data and transitions to the quiz screen."""
        if len(self.all_questions) < self.total_quiz_rounds:
             print(f"Error: Not enough questions. Found {len(self.all_questions)}, need {self.total_quiz_rounds}.")
             self.end_game()
             return

        self.go_to_screen('quiz_game')
        self.questions_for_round = random.sample(self.all_questions, self.total_quiz_rounds)
        Clock.schedule_once(self.start_quiz_round, 0.5)

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
        screen.ids.name_input.focus = True # Focus the TextInput for the VKeyboard

    def submit_score(self, player_name):
        """Saves the score and transitions to the leaderboard."""
        player_name = player_name.strip().upper()
        if not player_name:
            print("Player name is empty, not saving score.")
            # Optional: Add on-screen feedback here
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
        """Prepares and shows the instructions for the AGILITY game."""
        self.instruction_state = 'agility'
        screen = self.sm.get_screen('instructions')
        screen.update_content(
            title='[b]Como Jogar: Agilidade[/b]',
            body='Pressione o botão físico que acender o mais rápido que puder para marcar mais pontos!',
            button_text='COMEÇAR AGILIDADE'
        )
        self.go_to_screen('instructions')

    def proceed_from_instructions(self):
        """Called by the instruction screen button. Acts based on the current state."""
        if self.instruction_state == 'agility':
            self.start_game()
        elif self.instruction_state == 'quiz':
            self.start_quiz_section()

    def return_to_welcome(self):
        """Returns to the welcome screen and resets the game state."""
        self.score = 0
        self.current_agility_round = 0
        self.current_quiz_round = 0
        self.go_to_screen('welcome')