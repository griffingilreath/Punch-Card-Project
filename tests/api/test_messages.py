import subprocess
import time

# List of test messages
messages = [
    "HELLO WORLD",
    "PUNCH CARD TEST",
    "12345",
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "SYSTEM READY"
]

# Run each message with a short delay
for message in messages:
    print(f"\nTesting message: {message}")
    subprocess.run([
        "python3", "test_punch_card.py",
        "--test-message", message,
        "--led-delay", "0.1",
        "--message-delay", "2"
    ])
    time.sleep(1)  # Brief pause between messages 