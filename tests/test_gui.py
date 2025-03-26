#!/usr/bin/env python3
"""Test suite for GUI components."""

import argparse
import unittest
from punch_card import PunchCardGUI

class TestGUI(unittest.TestCase):
    def setUp(self):
        """Initialize GUI for tests."""
        self.gui = PunchCardGUI()

    def test_display_update(self):
        """Test display update functionality."""
        test_text = "TEST DISPLAY"
        self.gui.update_display(test_text)
        self.assertEqual(self.gui.get_display_text(), test_text)

    def test_button_states(self):
        """Test button enable/disable states."""
        self.gui.disable_input()
        self.assertFalse(self.gui.input_enabled())
        self.gui.enable_input()
        self.assertTrue(self.gui.input_enabled())

def check_display():
    """Run GUI display tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGUI)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test GUI components")
    parser.add_argument("--check-display", action="store_true", help="Run display tests")
    args = parser.parse_args()

    if args.check_display:
        check_display()
    else:
        unittest.main() 