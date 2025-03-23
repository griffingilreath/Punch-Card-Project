from punch_card import PunchCardDisplay
import time

def main():
    # Initialize the display
    display = PunchCardDisplay(
        rows=12,
        columns=80,
        led_delay=0.2,  # Faster display for testing
        brightness=0.5
    )
    
    try:
        # Show splash screen
        display.show_splash_screen()
        time.sleep(2)
        
        # Test messages
        test_messages = [
            "HELLO WORLD",
            "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG",
            "IBM PUNCH CARD SYSTEM READY",
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
            "SPECIAL CHARS: !@#$%^&*()_+-=[]{}|;:,.<>?"
        ]
        
        for message in test_messages:
            display.show_message(message)
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    finally:
        display.clear()

if __name__ == "__main__":
    main() 