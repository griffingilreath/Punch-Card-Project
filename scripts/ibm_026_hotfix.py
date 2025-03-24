#!/usr/bin/env python3
"""
IBM 026 Hotfix for Punch Card Project

This script identifies and provides instructions to fix syntax errors in the 
simple_display.py file. It also verifies the IBM 026 character encoding.
"""

import os
import sys
import re
import logging
import argparse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def check_format_punch_card():
    """Check if format_punch_card function has the correct IBM 026 encoding."""
    target_file = "simple_display.py"
    
    if not os.path.exists(target_file):
        logging.error(f"Cannot find {target_file} in the current directory")
        return False
        
    with open(target_file, 'r') as file:
        content = file.read()
    
    # Check for the function definition
    if "def format_punch_card" not in content:
        logging.error("format_punch_card function not found in the file")
        return False
    
    # Check for the correct IBM row mapping function
    if "def ibm_row_to_display_position" not in content:
        logging.error("ibm_row_to_display_position function not found in the file")
        return False
    
    # Check for specific character mappings
    if "'E': [12, 5]" not in content:
        logging.error("Incorrect mapping for character 'E'")
        return False

    if "'I': [12, 9]" not in content:
        logging.error("Incorrect mapping for character 'I'")
        return False
        
    if "'J': [11, 1]" not in content:
        logging.error("Incorrect mapping for character 'J'")
        return False
        
    if "'S': [0, 2]" not in content:
        logging.error("Incorrect mapping for character 'S'")
        return False
    
    logging.info("✅ format_punch_card function has the correct IBM 026 encoding")
    return True

def find_syntax_errors():
    """Find and report syntax errors in the simple_display.py file."""
    target_file = "simple_display.py"
    if not os.path.exists(target_file):
        logging.error(f"Cannot find {target_file} in the current directory")
        return False
    
    # List of common syntax error patterns
    error_patterns = [
        (r"try:(\s+)(?!except|finally)", "Missing except/finally block after try statement"),
        (r"except.*?:(\s+)(?!try|except|else|finally|[a-zA-Z0-9_])", "Empty except block"),
        (r"continue(?!.*?(?:for|while))", "Continue statement outside of loop"),
        (r"(?<=\n)[ \t]*[^ \t\n]+[ \t]*(?=\n[ \t]+except)", "Incorrect indentation before except block")
    ]
    
    with open(target_file, 'r') as file:
        content = file.read()
        lines = content.split('\n')
    
    errors = []
    for i, line in enumerate(lines):
        line_num = i + 1
        for pattern, message in error_patterns:
            if re.search(pattern, line):
                errors.append((line_num, line, message))
    
    if errors:
        logging.info(f"Found {len(errors)} potential syntax errors:")
        for line_num, line, message in errors:
            logging.info(f"Line {line_num}: {message}")
            logging.info(f"  {line.strip()}")
        return True
    else:
        logging.info("No common syntax errors found")
        return False

def apply_main_encoding_fix():
    """Instructions to fix the main program by using the standalone script."""
    logging.info("To apply the IBM 026 encoding fix, follow these steps:")
    logging.info("1. Copy the following files to a backup location:")
    logging.info("   - simple_display.py")
    logging.info("")
    logging.info("2. Use the standalone ibm_026_punch_card.py for testing until all syntax errors are fixed")
    logging.info("   - python3 ibm_026_punch_card.py --test-encoding")
    logging.info("   - python3 ibm_026_punch_card.py --show-alphabet")
    logging.info("   - python3 ibm_026_punch_card.py \"YOUR TEXT HERE\"")
    logging.info("")
    logging.info("3. To fix the syntax errors in simple_display.py, you'll need to correct:")
    logging.info("   - Mismatched try-except blocks")
    logging.info("   - Incorrect indentation")
    logging.info("   - Continue statements outside of loops")
    logging.info("")
    logging.info("4. Alternatively, consider creating a new patch release that incorporates")
    logging.info("   the fixed IBM 026 encoding from ibm_026_punch_card.py")

def main():
    """Main function to run the hotfix script."""
    parser = argparse.ArgumentParser(description="IBM 026 Hotfix for Punch Card Project")
    parser.add_argument("--check-encoding", action="store_true", help="Check if the format_punch_card function has the correct IBM 026 encoding")
    parser.add_argument("--find-errors", action="store_true", help="Find syntax errors in the simple_display.py file")
    parser.add_argument("--fix-instructions", action="store_true", help="Show instructions to fix the main program")
    
    args = parser.parse_args()
    
    if not (args.check_encoding or args.find_errors or args.fix_instructions):
        # If no arguments are provided, run all checks
        check_format_punch_card()
        find_syntax_errors()
        apply_main_encoding_fix()
    else:
        if args.check_encoding:
            check_format_punch_card()
        
        if args.find_errors:
            find_syntax_errors()
        
        if args.fix_instructions:
            apply_main_encoding_fix()

if __name__ == "__main__":
    main() 