
# API console functions to be added to simple_display.py

def update_api_console(message, level="info"):
    """Update the API console with a message.
    
    Args:
        message: The message to display
        level: The log level (info, warning, error, debug)
    """
    global api_console
    
    if not api_console:
        return
    
    # Convert log level to upper case for console
    level_upper = level.upper()
    
    # Special handling for some log levels
    if level.lower() == "api":
        level_upper = "API"
    
    # Log to the console
    api_console.log(message, level_upper)
