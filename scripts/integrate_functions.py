#!/usr/bin/env python3
"""
Function Integration Script - Integrates the generated animation methods and API console
functions directly into the main simple_display.py file.
"""

import os
import logging
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Target file
MAIN_FILE = "simple_display.py"
ANIMATION_FILE = "animation_methods.py"
API_CONSOLE_FILE = "api_console_functions.py"

def add_animation_methods():
    """Add animation methods to the PunchCardWidget class."""
    try:
        # Read animation methods
        if not os.path.exists(ANIMATION_FILE):
            logging.error(f"Animation methods file {ANIMATION_FILE} not found")
            return False
            
        with open(ANIMATION_FILE, 'r') as f:
            content = f.read()
            
        # Extract the methods (skip the comments)
        methods = re.findall(r'def ([^(]+)\([^)]*\):.*?(?=def|\Z)', content, re.DOTALL)
        if not methods:
            logging.error("Could not find any methods in animation file")
            return False
            
        # Get the methods content
        methods_content = []
        for method in methods:
            pattern = rf'def {method}\([^)]*\):.*?(?=def|\Z)'
            match = re.search(pattern, content, re.DOTALL)
            if match:
                methods_content.append(match.group(0))
        
        # Now read the main file
        with open(MAIN_FILE, 'r') as f:
            main_content = f.read()
            
        # Find the PunchCardWidget class
        widget_class_match = re.search(r'class PunchCardWidget\(.*?\):.*?(?=class|\Z)', main_content, re.DOTALL)
        if not widget_class_match:
            logging.error("Could not find PunchCardWidget class in main file")
            return False
            
        widget_class = widget_class_match.group(0)
        
        # Check if methods already exist
        methods_to_add = []
        for i, method in enumerate(methods):
            if f"def {method}" not in widget_class:
                methods_to_add.append(methods_content[i])
                
        if not methods_to_add:
            logging.info("All animation methods already exist in PunchCardWidget class")
            return True
            
        # Find the end of the class to add the methods
        # Look for the last method in the class
        last_method_match = re.search(r'(def [^(]+\([^)]*\):.*?)(?=class|\Z)', widget_class, re.DOTALL)
        if not last_method_match:
            logging.error("Could not find a place to add animation methods")
            return False
            
        # Get the indentation level of the last method
        indentation_match = re.search(r'^\s+', last_method_match.group(0), re.MULTILINE)
        indentation = indentation_match.group(0) if indentation_match else "    "
        
        # Add the indentation to each line of the methods
        indented_methods = []
        for method in methods_to_add:
            # Remove existing indentation
            method = re.sub(r'^\s+', '', method, flags=re.MULTILINE)
            # Add consistent indentation
            indented_method = '\n'.join(indentation + line if line.strip() else line 
                                       for line in method.split('\n'))
            indented_methods.append(indented_method)
            
        # Insert the methods at the end of the class
        updated_widget_class = widget_class.rstrip() + '\n' + '\n'.join(indented_methods)
        
        # Replace the old class with the updated one
        updated_main_content = main_content.replace(widget_class, updated_widget_class)
        
        # Write back to the main file
        with open(MAIN_FILE, 'w') as f:
            f.write(updated_main_content)
            
        logging.info(f"Added {len(methods_to_add)} animation methods to PunchCardWidget class")
        return True
        
    except Exception as e:
        logging.error(f"Failed to add animation methods: {e}")
        return False

def add_api_console_functions():
    """Add API console functions to the main file."""
    try:
        # Read API console functions
        if not os.path.exists(API_CONSOLE_FILE):
            logging.error(f"API console functions file {API_CONSOLE_FILE} not found")
            return False
            
        with open(API_CONSOLE_FILE, 'r') as f:
            content = f.read()
            
        # Extract the functions (skip the comments)
        functions = re.findall(r'def ([^(]+)\([^)]*\):.*?(?=def|\Z)', content, re.DOTALL)
        if not functions:
            logging.error("Could not find any functions in API console file")
            return False
            
        # Get the functions content
        functions_content = []
        for function in functions:
            pattern = rf'def {function}\([^)]*\):.*?(?=def|\Z)'
            match = re.search(pattern, content, re.DOTALL)
            if match:
                functions_content.append(match.group(0))
        
        # Now read the main file
        with open(MAIN_FILE, 'r') as f:
            main_content = f.read()
            
        # Check if functions already exist
        functions_to_add = []
        for i, function in enumerate(functions):
            if f"def {function}" not in main_content:
                functions_to_add.append(functions_content[i])
                
        if not functions_to_add:
            logging.info("All API console functions already exist in main file")
            return True
            
        # Find a good place to add the functions - after existing function definitions
        import_section_end = 0
        for i, line in enumerate(main_content.split('\n')):
            if line.startswith('import ') or line.startswith('from '):
                import_section_end = i
                
        # Find where the first class or function is defined
        class_or_func_match = re.search(r'^(class|def) ', main_content, re.MULTILINE)
        insertion_point = class_or_func_match.start() if class_or_func_match else import_section_end
        
        # Add global api_console declaration if it doesn't exist
        global_api_console = "# Global API console reference\napi_console = None\n\n"
        if "api_console = None" not in main_content:
            global_api_console_insertion = insertion_point
            main_content = (main_content[:global_api_console_insertion] + 
                           global_api_console + 
                           main_content[global_api_console_insertion:])
            insertion_point += len(global_api_console)
        
        # Add the functions
        functions_block = "\n# API Console Functions\n" + "\n".join(functions_to_add) + "\n\n"
        updated_main_content = (main_content[:insertion_point] + 
                               functions_block + 
                               main_content[insertion_point:])
        
        # Write back to the main file
        with open(MAIN_FILE, 'w') as f:
            f.write(updated_main_content)
            
        logging.info(f"Added {len(functions_to_add)} API console functions to main file")
        return True
        
    except Exception as e:
        logging.error(f"Failed to add API console functions: {e}")
        return False

def main():
    """Main function to integrate generated functions."""
    print("IBM 026 Punch Card Display - Function Integration")
    print("-----------------------------------------------")
    
    # Add animation methods
    if add_animation_methods():
        print("✅ Successfully added animation methods to PunchCardWidget class")
    else:
        print("❌ Failed to add animation methods")
        
    # Add API console functions
    if add_api_console_functions():
        print("✅ Successfully added API console functions to main file")
    else:
        print("❌ Failed to add API console functions")
        
    print("\nIntegration complete! You can now run the main program:")
    print("python3 simple_display.py")
    
if __name__ == "__main__":
    main() 