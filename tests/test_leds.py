#!/usr/bin/env python3
"""Test suite for LED hardware functionality."""

import argparse
import time
import unittest
from punch_card import LEDController

class TestLEDs(unittest.TestCase):
    def setUp(self):
        """Initialize LED controller for tests."""
        self.controller = LEDController()

    def test_led_sequence(self):
        """Test LED sequence patterns."""
        self.controller.test_pattern()
        time.sleep(1)  # Allow time to observe
        self.assertTrue(self.controller.verify_pattern())

    def test_individual_leds(self):
        """Test individual LED control."""
        for i in range(self.controller.num_leds):
            self.controller.set_led(i, True)
            time.sleep(0.1)
            self.assertTrue(self.controller.get_led_state(i))
            self.controller.set_led(i, False)

def run_hardware_tests():
    """Run LED hardware tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLEDs)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test LED hardware")
    parser.add_argument("--test", choices=["hardware"], help="Run hardware tests")
    args = parser.parse_args()

    if args.test == "hardware":
        run_hardware_tests()
    else:
        unittest.main() 