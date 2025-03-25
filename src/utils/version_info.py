#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Version Information Management
This module handles version information for the Punch Card Project.
"""

import os
import json
import subprocess
from pathlib import Path

# Current version (this will be used as a fallback)
VERSION = "0.6.2"

def get_version():
    """
    Get the current version of the application.
    
    Returns:
        str: The version string
    """
    # Try to get version from Git tag
    try:
        git_version = get_git_version()
        if git_version:
            return git_version.lstrip('v')
    except Exception:
        pass
    
    # Try to get version from settings file
    try:
        settings_version = get_settings_version()
        if settings_version:
            return settings_version
    except Exception:
        pass
    
    # Return hardcoded version as fallback
    return VERSION

def get_git_version():
    """
    Get the version from Git tags.
    
    Returns:
        str: The version from Git or None if not available
    """
    try:
        result = subprocess.run(
            ['git', 'describe', '--tags', '--abbrev=0'],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    
    return None

def get_settings_version():
    """
    Get the version from settings.json file.
    
    Returns:
        str: The version from settings or None if not available
    """
    try:
        # First check in the src directory
        project_root = Path(__file__).parent.parent.parent
        settings_paths = [
            project_root / 'src' / 'punch_card_settings.json',
            project_root / 'punch_card_settings.json'
        ]
        
        for settings_path in settings_paths:
            if settings_path.exists():
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                    if 'version' in settings:
                        return settings['version']
    except Exception:
        pass
    
    return None

if __name__ == "__main__":
    # Print version when script is run directly
    print(f"Punch Card Project v{get_version()}") 