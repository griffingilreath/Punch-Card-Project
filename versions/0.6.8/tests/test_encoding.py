#!/usr/bin/env python3
"""Test suite for punch card encoding validation."""

import argparse
import unittest
from punch_card import PunchCard, encode_text

class TestEncoding(unittest.TestCase):
    def test_basic_encoding(self):
        """Test basic text encoding to punch card format."""
        text = "HELLO WORLD"
        card = PunchCard()
        encoded = encode_text(text)
        self.assertEqual(len(encoded), len(text))
        self.assertTrue(all(c in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ .-" for c in encoded))

    def test_special_chars(self):
        """Test encoding of special characters."""
        text = "A-B.C"
        card = PunchCard()
        encoded = encode_text(text)
        self.assertEqual(len(encoded), len(text))
        self.assertTrue("-" in encoded)
        self.assertTrue("." in encoded)

def validate_encoding():
    """Run encoding validation tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEncoding)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test punch card encoding")
    parser.add_argument("--validate", action="store_true", help="Run encoding validation")
    args = parser.parse_args()

    if args.validate:
        validate_encoding()
    else:
        unittest.main() 