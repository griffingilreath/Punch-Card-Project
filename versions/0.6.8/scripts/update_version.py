#!/usr/bin/env python3
import json
import re

def update_readme_version():
    # Read version from settings
    with open('punch_card_settings.json', 'r') as f:
        settings = json.load(f)
        version = settings['version']
    
    # Read current README content
    with open('README.md', 'r') as f:
        content = f.read()
    
    # Update version in badge URL and text
    new_content = re.sub(
        r'version-[0-9]+\.[0-9]+\.[0-9]+-blue',
        f'version-{version}-blue',
        content
    )
    new_content = re.sub(
        r'/tag/v[0-9]+\.[0-9]+\.[0-9]+',
        f'/tag/v{version}',
        new_content
    )
    
    # Write updated content back to README
    with open('README.md', 'w') as f:
        f.write(new_content)

if __name__ == '__main__':
    update_readme_version() 