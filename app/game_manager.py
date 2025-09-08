import random
import time
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.screenmanager import ScreenManager
from app.hardware_io import HardwareController
from app.data_manager import DataManager
from app.audio_manager import AudioManager
from config import (AGILITY_BUTTONS_COUNT, AGILITY_MAX_SCORE, AGILITY_SCORE_PENALTY_PER_MS,
                   QUIZ_ROUNDS_COUNT, QUIZ_POINTS_PER_CORRECT)
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
        # CONFIGURABLE Agility State - now uses config values
        self.agility_buttons_to_press = AGILITY_BUTTONS_COUNT
        self.agility_buttons_remaining = self.agility_buttons_to_press
        self.agility_start_time = 0
        self.chronometer_event = None
        self.agility_in_progress = False
        self.target_led_index = -1
        
        # CONFIGURABLE Quiz State - now uses config values
        self.total_quiz_rounds = QUIZ_ROUNDS_COUNT
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
        self.agility_buttons_remaining = AGILITY_BUTTONS_COUNT # Reset using config value
        self.go_to_screen('instructions') # START AT INSTRUCTIONS
        # self.start_countdown() # This is now called from proceed_from_instructions

    def start_countdown(self):
        """Handles the 3, 2, 1 countdown with a single audio cue at the start."""
        if self.countdown_active:
            print("DEBUG: Countdown already active, skipping...")
            return  # Prevent multiple countdowns from starting
        self.countdown_active = True
        print("DEBUG: Starting countdown sequence...")
        
        self.go_to_screen('agility_game')
        screen = self.sm.get_screen('agility_game')
        
        # CRITICAL FIX: Reset overlay state completely before starting
        overlay = screen.ids.countdown_overlay
        
        # Cancel any existing animations on the overlay to prevent conflicts
        Animation.cancel_all(overlay)
        Animation.cancel_all(screen.ids.game_layout)
        
        # Reset overlay to fully visible and ready state
        overlay.opacity = 1.0
        overlay.text = ''
        print(f"DEBUG: Overlay reset - opacity: {overlay.opacity}, text: '{overlay.text}'")
        
        # Ensure the main game UI is hidden and ready
        screen.ids.game_layout.opacity = 0
        
        # --- CORRECTED LOGIC WITH PROPER STATE MANAGEMENT ---
        def update_text(number_or_go, dt):
            """Callback to update the text on screen."""
            overlay.text = str(number_or_go)
            print(f"DEBUG: Countdown text updated to '{overlay.text}', overlay opacity: {overlay.opacity}")

        def finish_countdown(dt):
            """Fades out the overlay and starts the game."""
            print("DEBUG: Finishing countdown, starting fade animations...")
            
            # Fade out the overlay and fade in the game UI
            fade_out_anim = Animation(opacity=0, d=0.3)
            fade_out_anim.start(overlay)
            
            # Create the fade-in animation with a callback
            fade_in_anim = Animation(opacity=1, d=0.3)
            
            def on_fade_complete(animation, widget):
                print("DEBUG: Fade animation complete, starting agility game...")
                # Start the actual game logic after animation completes
                self.start_agility_game()
                self.countdown_active = False # Reset the flag
                print("DEBUG: Countdown sequence completed, flag reset")
            
            fade_in_anim.bind(on_complete=on_fade_complete)
            fade_in_anim.start(screen.ids.game_layout)

        # --- SEQUENCE OF EVENTS ---
        # 1. Show '3' and play the single countdown sound immediately.
        overlay.text = '3'
        self.am.play('start')
        print("DEBUG: Countdown '3' displayed, sound played")

        # 2. Schedule the visual updates for '2' and '1'.
        Clock.schedule_once(lambda dt: update_text('2', dt), 1.0)
        Clock.schedule_once(lambda dt: update_text('1', dt), 2.0)
        
        # 3. Schedule the final transition to start the game.
        Clock.schedule_once(finish_countdown, 2.3) # A brief moment after "1"

    def start_agility_game(self, dt=None): # This method is now simpler
        """This method now ONLY starts the actual agility gameplay."""
        self.agility_buttons_remaining = AGILITY_BUTTONS_COUNT # Use config value
        
        # Update UI for the start of the round
        screen = self.sm.get_screen('agility_game')
        screen.ids.remaining_label.text = f'Restantes: {self.agility_buttons_remaining}'
        screen.ids.chronometer_label.text = '00:00'

        self.agility_start_time = time.perf_counter()
        self.chronometer_event = Clock.schedule_interval(self.update_chronometer, 1/60)
        self.trigger_next_led()
        
        print(f"DEBUG: Agility game started with {AGILITY_BUTTONS_COUNT} buttons to press")

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
                # CONFIGURABLE Scoring: max score minus penalty per millisecond
                self.score = max(0, AGILITY_MAX_SCORE - int(final_time * 1000 * AGILITY_SCORE_PENALTY_PER_MS))
                print(f"Agility finished in {final_time:.2f}s. Score: {self.score} (Max: {AGILITY_MAX_SCORE}, Penalty: {AGILITY_SCORE_PENALTY_PER_MS}/ms)")
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
        if len(self.all_questions) < QUIZ_ROUNDS_COUNT:
             print(f"Error: Not enough questions. Found {len(self.all_questions)}, need {QUIZ_ROUNDS_COUNT}.")
             self.end_game()
             return

        # Reset quiz state completely
        self.current_quiz_round = 0
        self.quiz_in_progress = False
        
        self.go_to_screen('quiz_game')
        self.questions_for_round = random.sample(self.all_questions, QUIZ_ROUNDS_COUNT)
        
        print(f"DEBUG: Quiz section started with {QUIZ_ROUNDS_COUNT} questions")
        
        # Reset all quiz buttons to default state before starting
        screen = self.sm.get_screen('quiz_game')
        answer_buttons = [screen.ids.option_a, screen.ids.option_b, screen.ids.option_c, screen.ids.option_d]
        for button in answer_buttons:
            button.disabled = False
            button.button_bg_color = (216/255, 206/255, 205/255, 1)  # Default light gray
            button.text = ""
        
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

    def check_answer_by_id(self, button_id):
        """
        NOVA SOLUÇÃO: Recebe o ID do botão diretamente, contornando bug do Kivy.
        """
        if not self.quiz_in_progress: return
        self.quiz_in_progress = False

        screen = self.sm.get_screen('quiz_game')
        correct_answer = self.current_question_data['correct_answer']
        
        # Obter o botão correto pelo ID
        selected_button = getattr(screen.ids, button_id)
        selected_answer = selected_button.text
        is_correct = (selected_answer == correct_answer)

        print(f"\n=== DEBUG SOLUÇÃO POR ID ===")
        print(f"ID recebido: {button_id}")
        print(f"Botão selecionado: {selected_button}")
        print(f"Texto do botão: '{selected_answer}'")
        print(f"Posição do botão: {selected_button.pos}")
        print(f"Resposta correta: '{correct_answer}'")
        print(f"Está correto: {is_correct}")
        print("=== END DEBUG ===\n")

        # --- Core Logic with CONFIGURABLE scoring ---
        if is_correct:
            self.score += QUIZ_POINTS_PER_CORRECT
            self.am.play('correct')
            print(f"Quiz answer: Correct! (+{QUIZ_POINTS_PER_CORRECT} points)")
        else:
            self.am.play('wrong')
            print("Quiz answer: Incorrect!")

        # --- Delegation to Presentation Layer ---
        screen.show_feedback(
            is_correct=is_correct,
            correct_answer_text=correct_answer,
            selected_widget=selected_button
        )

        # Schedule the next round, allowing the player 2.5 seconds to absorb the feedback.
        Clock.schedule_once(self.start_quiz_round, 2.5)

    # Manter método antigo para compatibilidade (caso seja chamado de outro lugar)
    def check_answer(self, selected_button_widget):
        """Método legado - redireciona para nova implementação"""
        # Tentar identificar o ID pelo widget (fallback)
        screen = self.sm.get_screen('quiz_game')
        if selected_button_widget == screen.ids.option_a:
            self.check_answer_by_id('option_a')
        elif selected_button_widget == screen.ids.option_b:
            self.check_answer_by_id('option_b')
        elif selected_button_widget == screen.ids.option_c:
            self.check_answer_by_id('option_c')
        elif selected_button_widget == screen.ids.option_d:
            self.check_answer_by_id('option_d')
        else:
            print("ERRO: Não foi possível identificar o botão clicado")

    def end_game(self):
        """Called after the last quiz round. Transitions to the Score screen."""
        print(f"Game over! Final Score: {self.score}")
        self.go_to_screen('score')
        screen = self.sm.get_screen('score')
        screen.ids.final_score_label.text = f'Sua Pontuação Final: {self.score}'
        screen.ids.name_input.text = '' # Clear input field
        screen.ids.name_input.focus = True # Focus the TextInput for the VKeyboard
        
        # Bind text validation to limit input length
        screen.ids.name_input.bind(text=self._validate_name_input)

    def _validate_name_input(self, instance, text):
        """Validates and limits the name input to reasonable length for initials."""
        # Limit to 8 characters maximum for initials
        max_length = 8
        if len(text) > max_length:
            instance.text = text[:max_length]
        
        # Convert to uppercase automatically
        if text != text.upper():
            instance.text = text.upper()

    def virtual_key_press(self, key_value):
        """Handles virtual keyboard key presses with proper functionality."""
        if self.sm.current != 'score':
            return
            
        screen = self.sm.get_screen('score')
        name_input = screen.ids.name_input
        
        if key_value == 'BACKSPACE':
            # Remove last character
            name_input.do_backspace()
        elif key_value == 'SPACE':
            # Add space character
            name_input.insert_text(' ')
        elif key_value == 'ENTER':
            # Submit the score
            self.submit_score(name_input.text)
        else:
            # Regular character input
            name_input.insert_text(key_value)

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
        print("DEBUG: Returning to welcome, resetting all game state...")
        
        self.score = 0
        self.current_agility_round = 0
        self.current_quiz_round = 0
        
        # Reset countdown flag to allow countdown on next play
        self.countdown_active = False
        
        # Reset instruction state
        self.instruction_state = None
        
        # Reset quiz and agility states
        self.quiz_in_progress = False
        self.agility_in_progress = False
        
        # Cancel any active chronometer
        if self.chronometer_event:
            self.chronometer_event.cancel()
            self.chronometer_event = None
            
        # CRITICAL FIX: Reset countdown overlay state for next game
        try:
            agility_screen = self.sm.get_screen('agility_game')
            overlay = agility_screen.ids.countdown_overlay
            
            # Cancel any pending animations
            Animation.cancel_all(overlay)
            Animation.cancel_all(agility_screen.ids.game_layout)
            
            # Reset overlay to initial state
            overlay.opacity = 1.0
            overlay.text = ''
            agility_screen.ids.game_layout.opacity = 0
            
            print("DEBUG: Countdown overlay state reset for next game")
        except Exception as e:
            print(f"DEBUG: Error resetting overlay state: {e}")
            
        # Turn off all LEDs
        self.hw.turn_off_all_leds()
        
        self.go_to_screen('welcome')
        print("DEBUG: Welcome screen transition complete")