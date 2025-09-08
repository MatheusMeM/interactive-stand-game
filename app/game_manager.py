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
        # NEW/REPURPOSED Agility State
        self.agility_buttons_to_press = 10 # Total buttons to hit
        self.agility_buttons_remaining = self.agility_buttons_to_press
        self.agility_start_time = 0
        self.chronometer_event = None
        self.agility_in_progress = False
        self.target_led_index = -1
        
        self.total_quiz_rounds = 3
        self.current_quiz_round = 0
        self.current_question_data = None
        self.quiz_in_progress = False
        self.instruction_state = None # <-- NEW state variable
        self.countdown_active = False  # Guard flag to prevent multiple countdowns

        print("GameManager initialized with HardwareController and DataManager.")

    def start_game(self):
        """Resets game state and starts the countdown for the agility game."""
        self.score = 0
        self.current_quiz_round = 0
        self.agility_buttons_remaining = self.agility_buttons_to_press # Reset counter
        self.go_to_screen('instructions') # START AT INSTRUCTIONS
        # self.start_countdown() # This is now called from proceed_from_instructions

    def start_countdown(self):
        """Handles the 3, 2, 1 countdown with a single audio cue at the start."""
        if self.countdown_active:
            return  # Prevent multiple countdowns from starting
        self.countdown_active = True
        
        self.go_to_screen('agility_game')
        screen = self.sm.get_screen('agility_game')
        
        # Ensure the main game UI is hidden and the overlay is ready
        screen.ids.game_layout.opacity = 0
        overlay = screen.ids.countdown_overlay
        
        # --- NEW, SIMPLIFIED LOGIC ---
        def update_text(number_or_go, dt):
            """Callback to update the text on screen."""
            overlay.text = str(number_or_go)

        def finish_countdown(dt):
            """Fades out the overlay and starts the game."""
            # Fade out the overlay and fade in the game UI
            Animation(opacity=0, d=0.3).start(overlay)
            
            # Create the fade-in animation with a callback
            fade_in_anim = Animation(opacity=1, d=0.3)
            
            def on_fade_complete(animation, widget):
                # Start the actual game logic after animation completes
                self.start_agility_game()
                self.countdown_active = False # Reset the flag
            
            fade_in_anim.bind(on_complete=on_fade_complete)
            fade_in_anim.start(screen.ids.game_layout)

        # --- SEQUENCE OF EVENTS ---
        # 1. Show '3' and play the single countdown sound immediately.
        overlay.text = '3'
        self.am.play('start')

        # 2. Schedule the visual updates for '2' and '1'.
        Clock.schedule_once(lambda dt: update_text('2', dt), 1.0)
        Clock.schedule_once(lambda dt: update_text('1', dt), 2.0)
        
        # 3. Schedule the final transition to start the game.
        Clock.schedule_once(finish_countdown, 2.3) # A brief moment after "1"

    def start_agility_game(self, dt=None): # This method is now simpler
        """This method now ONLY starts the actual agility gameplay."""
        self.agility_buttons_remaining = self.agility_buttons_to_press
        
        # Update UI for the start of the round
        screen = self.sm.get_screen('agility_game')
        screen.ids.remaining_label.text = f'Restantes: {self.agility_buttons_remaining}'
        screen.ids.chronometer_label.text = '00:00'

        self.agility_start_time = time.perf_counter()
        self.chronometer_event = Clock.schedule_interval(self.update_chronometer, 1/60)
        self.trigger_next_led()

    def update_chronometer(self, dt):
        """Updates the chronometer label on screen."""
        elapsed_time = time.perf_counter() - self.agility_start_time
        seconds = int(elapsed_time)
        milliseconds = int((elapsed_time * 100) % 100)
        self.sm.get_screen('agility_game').ids.chronometer_label.text = f'{seconds:02}:{milliseconds:02}'

    def trigger_next_led(self):
        """Turns on a new random LED."""
        self.target_led_index = random.randint(0, len(self.hw.leds) - 1)
        self.hw.turn_on_led(self.target_led_index)
        self.agility_in_progress = True

    def on_button_press(self, pressed_index):
        """Callback for the new chronometer-based game."""
        if not self.agility_in_progress: return
        
        if pressed_index == self.target_led_index:
            self.agility_in_progress = False # Prevent multiple presses
            self.hw.turn_off_led(self.target_led_index)
            self.am.play('correct')
            
            self.agility_buttons_remaining -= 1
            self.sm.get_screen('agility_game').ids.remaining_label.text = f'Restantes: {self.agility_buttons_remaining}'

            if self.agility_buttons_remaining <= 0:
                # GAME OVER
                self.chronometer_event.cancel()
                final_time = time.perf_counter() - self.agility_start_time
                # Scoring: 20000 points minus 100 points per tenth of a second
                self.score = max(0, 20000 - int(final_time * 1000))
                print(f"Agility finished in {final_time:.2f}s. Score: {self.score}")
                self.end_agility_section()
            else:
                # Trigger the next button
                self.trigger_next_led()
        # If wrong button is pressed, we do nothing. The player must find the right one.

    def end_agility_section(self):
        """Called after agility. Prepares and shows instructions for the QUIZ game."""
        print("Agility section finished. Showing Quiz instructions.")
        self.hw.turn_off_all_leds()
        self.instruction_state = 'quiz'
        screen = self.sm.get_screen('instructions')
        screen.update_content(
            title='Como Jogar: Quiz',
            body='\n\n• Uma pergunta sobre o IBP aparecerá no centro da tela.\n\n• Quatro opções de resposta serão exibidas logo abaixo.\n\n• Toque na resposta que você considera correta para acumular pontos.\n\n',
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

    def check_answer(self, selected_button_widget):
        """
        Orchestrates the answer checking and delegates the feedback presentation.
        This is the central logic hub for a quiz round.
        """
        if not self.quiz_in_progress: return
        self.quiz_in_progress = False

        screen = self.sm.get_screen('quiz_game')
        correct_answer = self.current_question_data['correct_answer']
        selected_answer = selected_button_widget.text
        is_correct = (selected_answer == correct_answer)

        # --- Core Logic ---
        if is_correct:
            self.score += 500
            self.am.play('correct')
            print("Quiz answer: Correct!")
        else:
            self.am.play('wrong')
            print("Quiz answer: Incorrect!")

        # --- Delegation to Presentation Layer ---
        # Command the screen to show the comprehensive feedback.
        screen.show_feedback(
            is_correct=is_correct,
            correct_answer_text=correct_answer,
            selected_widget=selected_button_widget
        )

        # Schedule the next round, allowing the player 2.5 seconds to absorb the feedback.
        Clock.schedule_once(self.start_quiz_round, 2.5)

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
            title='Como Jogar: Agilidade',
            body='\n\n• Observe o painel de botões. \n\n • Quando uma luz acender, pressione o botão correspondente imediatamente. \n\n • Após o acerto, a luz se apaga e um novo botão acenderá, iniciando a próxima rodada.\n',
            button_text='COMEÇAR AGILIDADE'
        )
        self.go_to_screen('instructions')

    def skip_agility_game(self):
        """Ends the agility game prematurely, called by 'q' key."""
        if self.sm.current == 'agility_game':
            print("Agility game skipped by user.")
            if self.chronometer_event:
                self.chronometer_event.cancel()
            self.score = 0 # Set agility score to 0
            self.end_agility_section()
    
    def proceed_from_instructions(self):
        """Called by the instruction screen button. Acts based on the current state."""
        if self.instruction_state == 'agility':
            # --- CHANGED: Don't start the game directly, start the countdown ---
            self.start_countdown()
        elif self.instruction_state == 'quiz':
            self.start_quiz_section()

    def return_to_welcome(self):
        """Returns to the welcome screen and resets the game state."""
        self.score = 0
        self.current_agility_round = 0
        self.current_quiz_round = 0
        self.go_to_screen('welcome')