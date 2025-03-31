#!/usr/bin/env python3
"""
Simplified Branch Helper

This script implements the simplified three-branch strategy for the Punch Card Project:
- main: Production-ready code
- stable: Pre-release staging branch
- testing: Active development branch

Usage:
  python branch_helper.py <command> [options]

Commands:
  status          - Show current branch status
  create-tag      - Create a new version tag
  push-to-stable  - Merge testing into stable
  push-to-main    - Merge stable into main
  create-release  - Create a release by tagging main
"""

import os
import sys
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
import re
from typing import List, Tuple, Optional


class BranchHelper:
    """Helper for managing the simplified branch strategy"""
    
    def __init__(self):
        self.project_root = Path(os.getcwd())
        
        # Check if this is a git repository
        if not (self.project_root / '.git').exists():
            print(f"Error: {self.project_root} is not a Git repository")
            print("Please run this script from the root of the project repository.")
            sys.exit(1)
    
    def run_git_command(self, args: List[str], check: bool = True) -> Tuple[int, str]:
        """Run a git command and return exit code and output"""
        cmd = ["git"] + args
        result = subprocess.run(cmd, cwd=self.project_root, 
                              capture_output=True, text=True, check=False)
        if check and result.returncode != 0:
            print(f"Error running git command: {' '.join(cmd)}")
            print(f"Error message: {result.stderr}")
            sys.exit(result.returncode)
        return result.returncode, result.stdout.strip()
    
    def get_current_branch(self) -> str:
        """Get the current git branch name"""
        _, branch = self.run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])
        return branch
    
    def get_branches(self) -> List[str]:
        """Get all local branches"""
        _, output = self.run_git_command(["branch"])
        branches = []
        for line in output.split('\n'):
            if line.strip():
                # Remove the asterisk and spaces
                branch = line.strip('* ').strip()
                branches.append(branch)
        return branches
    
    def get_tags(self) -> List[str]:
        """Get all tags"""
        _, output = self.run_git_command(["tag"])
        return [tag for tag in output.split('\n') if tag.strip()]
    
    def check_branch_exists(self, branch_name: str) -> bool:
        """Check if a branch exists"""
        branches = self.get_branches()
        return branch_name in branches
    
    def ensure_branch_exists(self, branch_name: str, base_branch: str = "main") -> None:
        """Ensure a branch exists, creating it if necessary"""
        if not self.check_branch_exists(branch_name):
            print(f"Branch {branch_name} does not exist. Creating from {base_branch}...")
            self.run_git_command(["checkout", base_branch])
            self.run_git_command(["checkout", "-b", branch_name])
            print(f"Created branch {branch_name}")
    
    def show_status(self) -> int:
        """Show the current status of branches and tags"""
        current_branch = self.get_current_branch()
        branches = self.get_branches()
        tags = self.get_tags()
        
        print(f"\n=== Punch Card Project Branch Status ===\n")
        print(f"Current branch: {current_branch}")
        print(f"\nBranches:")
        
        for branch in ["main", "stable", "testing"]:
            prefix = "*" if branch == current_branch else " "
            if branch in branches:
                print(f"{prefix} {branch}")
            else:
                print(f"  {branch} (not created yet)")
        
        print(f"\nOther branches:")
        for branch in sorted(branches):
            if branch not in ["main", "stable", "testing"]:
                prefix = "*" if branch == current_branch else " "
                print(f"{prefix} {branch}")
        
        print(f"\nTags (newest first):")
        for tag in sorted(tags, reverse=True)[:5]:  # Show most recent 5 tags
            print(f"  {tag}")
        
        if len(tags) > 5:
            print(f"  ... and {len(tags) - 5} more")
        
        print(f"\nNext steps:")
        print("  - To push changes to stable: python branch_helper.py push-to-stable")
        print("  - To push changes to main: python branch_helper.py push-to-main")
        print("  - To create a new release: python branch_helper.py create-release <version>")
        
        return 0

    def push_to_stable(self) -> int:
        """Merge testing into stable"""
        # Ensure both branches exist
        self.ensure_branch_exists("stable", "main")
        self.ensure_branch_exists("testing", "stable")
        
        current_branch = self.get_current_branch()
        
        # First, make sure testing is up to date
        print("Checking out testing branch...")
        self.run_git_command(["checkout", "testing"])
        
        # Perform the merge
        print("Merging testing into stable...")
        self.run_git_command(["checkout", "stable"])
        self.run_git_command(["merge", "--no-ff", "testing", "-m", "Merge testing into stable"])
        
        print("\nSuccessfully merged testing into stable!")
        print("\nNext steps:")
        print("  - Test the stable branch thoroughly")
        print("  - When ready for production: python branch_helper.py push-to-main")
        
        # Return to original branch
        if current_branch not in ["testing", "stable"]:
            self.run_git_command(["checkout", current_branch])
            
        return 0
    
    def push_to_main(self) -> int:
        """Merge stable into main"""
        # Ensure branches exist
        self.ensure_branch_exists("main")
        self.ensure_branch_exists("stable", "main")
        
        current_branch = self.get_current_branch()
        
        # Perform the merge
        print("Merging stable into main...")
        self.run_git_command(["checkout", "main"])
        self.run_git_command(["merge", "--no-ff", "stable", "-m", "Merge stable into main"])
        
        print("\nSuccessfully merged stable into main!")
        print("\nNext steps:")
        print("  - Create a release tag: python branch_helper.py create-release <version>")
        
        # Return to original branch
        if current_branch != "main":
            self.run_git_command(["checkout", current_branch])
            
        return 0
    
    def create_release(self, version: str) -> int:
        """Create a release by tagging the main branch"""
        # Validate version format
        if not re.match(r'^[0-9]+\.[0-9]+\.[0-9]+$', version):
            print("Error: Version must be in format MAJOR.MINOR.PATCH (e.g., 1.0.0)")
            return 1
        
        tag_name = f"v{version}"
        
        # Check if tag already exists
        if tag_name in self.get_tags():
            print(f"Error: Tag {tag_name} already exists")
            return 1
        
        # Switch to main branch
        print("Switching to main branch...")
        self.run_git_command(["checkout", "main"])
        
        # Create annotated tag
        print(f"Creating tag {tag_name}...")
        release_date = datetime.now().strftime("%Y-%m-%d")
        tag_message = f"Version {version} released on {release_date}"
        self.run_git_command(["tag", "-a", tag_name, "-m", tag_message])
        
        # Update CHANGELOG.md
        self._update_changelog(version, release_date)
        
        print(f"\nSuccessfully created release {tag_name}!")
        print("\nNext steps:")
        print(f"  - Push tag to remote: git push origin {tag_name}")
        print("  - Push branches: git push origin main stable testing")
        
        return 0
    
    def _update_changelog(self, version: str, release_date: str) -> None:
        """Update the CHANGELOG.md file with the new release"""
        changelog_path = self.project_root / "CHANGELOG.md"
        if not changelog_path.exists():
            print("Warning: CHANGELOG.md not found. Skipping changelog update.")
            return
        
        try:
            with open(changelog_path, 'r') as f:
                content = f.readlines()
            
            # Update version date if it already exists
            version_line_idx = -1
            for i, line in enumerate(content):
                if f"## [{version}]" in line:
                    version_line_idx = i
                    break
            
            if version_line_idx != -1:
                # Update existing version entry
                date_line = content[version_line_idx]
                if "unreleased" in date_line.lower() or not re.search(r'\d{4}-\d{2}-\d{2}', date_line):
                    content[version_line_idx] = f"## [{version}] - {release_date}\n"
                    with open(changelog_path, 'w') as f:
                        f.writelines(content)
                    print(f"Updated release date for version {version} in CHANGELOG.md")
            else:
                print(f"Warning: Version {version} not found in CHANGELOG.md")
        
        except Exception as e:
            print(f"Error updating CHANGELOG.md: {e}")


def main():
    parser = argparse.ArgumentParser(description="Simplified Branch Helper for Punch Card Project")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Status command
    subparsers.add_parser('status', help='Show branch status')
    
    # Push to stable command
    subparsers.add_parser('push-to-stable', help='Merge testing into stable')
    
    # Push to main command
    subparsers.add_parser('push-to-main', help='Merge stable into main')
    
    # Create release command
    create_release_parser = subparsers.add_parser('create-release', help='Create a release tag')
    create_release_parser.add_argument('version', help='Version number (e.g., 1.0.0)')
    
    args = parser.parse_args()
    
    helper = BranchHelper()
    
    if args.command == 'status':
        return helper.show_status()
    elif args.command == 'push-to-stable':
        return helper.push_to_stable()
    elif args.command == 'push-to-main':
        return helper.push_to_main()
    elif args.command == 'create-release':
        return helper.create_release(args.version)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main()) 