from gpiozero import Button, LED
from config import BUTTON_PINS, RELAY_PINS

class HardwareController:
    """
    Hardware Abstraction Layer (HAL) for all GPIO interactions.
    This class manages the physical buttons and LEDs (via relays).
    """
    def __init__(self):
        if not BUTTON_PINS or not RELAY_PINS:
            raise ValueError("GPIO pins are not defined in config.py. Please configure them before running.")

        self.buttons = [Button(pin) for pin in BUTTON_PINS]
        
        # --- THIS IS THE CRITICAL CHANGE ---
        # Initialize LEDs with active_high=False to handle active-low relays.
        # Now, .on() will send a LOW signal, and .off() will send a HIGH signal.
        self.leds = [LED(pin, active_high=False) for pin in RELAY_PINS]
        # --- END OF CHANGE ---
        
        print("HardwareController initialized for ACTIVE-LOW relays.")
        print(f" - {len(self.buttons)} buttons on pins: {BUTTON_PINS}")
        print(f" - {len(self.leds)} LEDs (relays) on pins: {RELAY_PINS}")

    def set_button_callback(self, callback_func):
        """
        Assigns a single callback function to all button press events.
        The callback function will receive the button's index.
        """
        for i, button in enumerate(self.buttons):
            button.when_pressed = lambda b, index=i: callback_func(index)
            
    def turn_on_led(self, index):
        """Turns on a specific LED by its index (0-11)."""
        if 0 <= index < len(self.leds):
            self.leds[index].on()

    def turn_off_led(self, index):
        """Turns off a specific LED by its index (0-11)."""
        if 0 <= index < len(self.leds):
            self.leds[index].off()

    def turn_off_all_leds(self):
        """Turns off all LEDs safely, checking if they're still open."""
        for i, led in enumerate(self.leds):
            try:
                if not led.closed:
                    led.off()
            except Exception as e:
                print(f"Warning: Could not turn off LED {i}: {e}")

    def cleanup(self):
        """Releases all GPIO resources safely."""
        print("Cleaning up GPIO resources...")
        
        # Safely turn off all LEDs
        try:
            self.turn_off_all_leds()
        except Exception as e:
            print(f"Warning during LED cleanup: {e}")
        
        # Safely close all buttons
        for i, button in enumerate(self.buttons):
            try:
                if not button.closed:
                    button.close()
            except Exception as e:
                print(f"Warning: Could not close button {i}: {e}")
        
        # Safely close all LEDs
        for i, led in enumerate(self.leds):
            try:
                if not led.closed:
                    led.close()
            except Exception as e:
                print(f"Warning: Could not close LED {i}: {e}")
        
        print("GPIO resources cleaned up.")