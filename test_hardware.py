import time
from app.hardware_io import HardwareController

# --- IMPORTANT ---
# Before running, you MUST populate the BUTTON_PINS and RELAY_PINS lists
# in your config.py file with the actual BCM pin numbers you have wired.
# For example:
# BUTTON_PINS = [2, 3, 4, 17, 27, 22, 10, 9, 11, 5, 6, 13]
# RELAY_PINS = [14, 15, 18, 23, 24, 25, 8, 7, 12, 16, 20, 21]

def handle_button_press(button_index):
    """This function is called when any button is pressed."""
    print(f"--- Button {button_index} pressed! ---")
    # For a fun test, let's light up the corresponding LED
    controller.turn_on_led(button_index)
    time.sleep(0.2) # Keep it lit for a moment
    controller.turn_off_led(button_index)

if __name__ == "__main__":
    print("Starting hardware test script. Press Ctrl+C to exit.")
    
    try:
        controller = HardwareController()
        controller.set_button_callback(handle_button_press)

        print("\nCycling all LEDs on and off...")
        for i in range(len(controller.leds)):
            print(f"Turning on LED {i}")
            controller.turn_on_led(i)
            time.sleep(0.2)
            controller.turn_off_led(i)
        
        print("\nHardware test running. Press buttons to see feedback.")
        print("The program will wait for button presses indefinitely.")
        
        # The 'pause()' function keeps the script alive to listen for events.
        from signal import pause
        pause()

    except KeyboardInterrupt:
        print("\nExit signal received.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        # This ensures GPIOs are released no matter how the script exits.
        if controller is not None:
            print("Cleaning up GPIO resources.")
            controller.cleanup()
        print("Script finished.")