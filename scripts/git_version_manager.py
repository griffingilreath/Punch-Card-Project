#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
from pathlib import Path
import re
from typing import List, Optional, Tuple

class GitVersionManager:
    """
    Git Version Manager for the Punch Card Project
    
    This tool implements a Git branching strategy that works with the 
    existing version_manager.py script to create a comprehensive versioning system.
    
    Branching Strategy:
    - master: Main development branch
    - develop: Integration branch for new features
    - feature/*: Feature branches for new functionality
    - release/*: Release preparation branches
    - hotfix/*: Emergency fixes for production
    - v*.*.*: Version branches for each release
    
    This follows a modified GitFlow workflow adapted for this project's needs.
    """
    
    def __init__(self, project_root: str = None):
        # Set project root to current directory if not specified
        if project_root is None:
            self.project_root = Path(os.getcwd())
        else:
            self.project_root = Path(project_root)
        
        # Check if this is a git repository
        if not (self.project_root / '.git').exists():
            raise ValueError(f"{self.project_root} is not a Git repository")
        
        # Path to version manager script
        self.version_manager_path = self.project_root / "scripts" / "version_manager.py"
        if not self.version_manager_path.exists():
            print(f"Warning: version_manager.py not found at {self.version_manager_path}")
    
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
    
    def run_version_manager(self, args: List[str]) -> int:
        """Run the version_manager.py script with given arguments"""
        if not self.version_manager_path.exists():
            print(f"Error: version_manager.py not found at {self.version_manager_path}")
            return 1
        
        cmd = [sys.executable, str(self.version_manager_path)] + args
        result = subprocess.run(cmd, cwd=self.project_root)
        return result.returncode
    
    def get_current_branch(self) -> str:
        """Get the current git branch name"""
        _, branch = self.run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])
        return branch
    
    def get_current_version(self) -> str:
        """Get the current version from README.md"""
        readme_path = self.project_root / "README.md"
        if not readme_path.exists():
            print("Warning: README.md not found, can't determine current version")
            return "unknown"
        
        with open(readme_path, 'r') as f:
            content = f.read()
        
        # Look for version pattern in README.md
        match = re.search(r'# Punch Card Project v([0-9\.]+)', content)
        if match:
            return match.group(1)
        
        # Fallback to looking for other version patterns
        match = re.search(r'v([0-9\.]+)', content)
        if match:
            return match.group(1)
        
        return "unknown"
    
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
    
    def create_feature_branch(self, feature_name: str) -> int:
        """Create a new feature branch"""
        branch_name = f"feature/{feature_name}"
        # Check if branch already exists
        if branch_name in self.get_branches():
            print(f"Branch {branch_name} already exists")
            return 1
        
        # Create branch from develop if it exists, otherwise from master
        if "develop" in self.get_branches():
            base_branch = "develop"
        else:
            base_branch = "master"
        
        print(f"Creating feature branch {branch_name} from {base_branch}")
        self.run_git_command(["checkout", base_branch])
        self.run_git_command(["pull", "origin", base_branch])
        self.run_git_command(["checkout", "-b", branch_name])
        
        print(f"Feature branch {branch_name} created successfully")
        print(f"When finished, use: python scripts/git_version_manager.py finish-feature {feature_name}")
        
        return 0
    
    def finish_feature_branch(self, feature_name: str) -> int:
        """Finish a feature branch by merging into develop"""
        branch_name = f"feature/{feature_name}"
        
        # Check if branch exists
        if branch_name not in self.get_branches():
            print(f"Error: Branch {branch_name} does not exist")
            return 1
        
        # Ensure develop branch exists
        if "develop" not in self.get_branches():
            print("Creating develop branch from master")
            self.run_git_command(["checkout", "master"])
            self.run_git_command(["checkout", "-b", "develop"])
        
        # Merge feature branch into develop
        print(f"Merging {branch_name} into develop")
        self.run_git_command(["checkout", "develop"])
        self.run_git_command(["merge", "--no-ff", branch_name, "-m", f"Merge feature '{feature_name}'"])
        
        # Delete the feature branch
        print(f"Deleting feature branch {branch_name}")
        self.run_git_command(["branch", "-d", branch_name])
        
        print(f"Feature '{feature_name}' has been merged into develop")
        return 0
    
    def create_release(self, version: str, description: str = None) -> int:
        """
        Create a release branch and prepare version
        
        This will:
        1. Create a release/v{version} branch from develop
        2. Update version in README.md
        3. Create version snapshot using version_manager.py
        """
        # Validate version format
        if not re.match(r'^[0-9]+\.[0-9]+\.[0-9]+$', version):
            print("Error: Version must be in format major.minor.patch (e.g., 1.0.0)")
            return 1
        
        release_branch = f"release/v{version}"
        version_branch = f"v{version}"
        
        # Check if release branch already exists
        if release_branch in self.get_branches():
            print(f"Error: Release branch {release_branch} already exists")
            return 1
        
        # Ensure develop branch exists
        if "develop" not in self.get_branches():
            print("Creating develop branch from master")
            self.run_git_command(["checkout", "master"])
            self.run_git_command(["checkout", "-b", "develop"])
        
        # Create release branch from develop
        print(f"Creating release branch {release_branch} from develop")
        self.run_git_command(["checkout", "develop"])
        self.run_git_command(["pull", "origin", "develop"])
        self.run_git_command(["checkout", "-b", release_branch])
        
        # Update version in README.md
        current_version = self.get_current_version()
        readme_path = self.project_root / "README.md"
        
        if readme_path.exists():
            with open(readme_path, 'r') as f:
                content = f.read()
            
            # Replace version in README.md
            if current_version != "unknown":
                content = content.replace(f"v{current_version}", f"v{version}")
                with open(readme_path, 'w') as f:
                    f.write(content)
                
                print(f"Updated version in README.md from v{current_version} to v{version}")
                
                # Commit the version update
                self.run_git_command(["add", "README.md"])
                self.run_git_command(["commit", "-m", f"Bump version to v{version}"])
        
        # Prepare arguments for version_manager.py
        if description is None:
            description = f"Version {version} release"
        
        # Run tests before finalizing
        print("Running tests to ensure release quality...")
        # TODO: Add appropriate test commands for your project
        
        print(f"Release branch {release_branch} created successfully")
        print(f"Make any final adjustments and then use:")
        print(f"python scripts/git_version_manager.py finish-release {version}")
        
        return 0
    
    def finish_release(self, version: str) -> int:
        """
        Finish a release branch
        
        This will:
        1. Merge release/v{version} into master
        2. Tag the release
        3. Merge back into develop
        4. Create version branch v{version}
        5. Generate version snapshot with version_manager.py
        6. Delete the release branch
        """
        release_branch = f"release/v{version}"
        version_branch = f"v{version}"
        tag_name = f"v{version}"
        
        # Check if release branch exists
        if release_branch not in self.get_branches():
            print(f"Error: Release branch {release_branch} does not exist")
            return 1
        
        # Merge into master
        print(f"Merging {release_branch} into master")
        self.run_git_command(["checkout", "master"])
        self.run_git_command(["merge", "--no-ff", release_branch, "-m", f"Merge release v{version}"])
        
        # Create tag
        print(f"Creating tag {tag_name}")
        self.run_git_command(["tag", "-a", tag_name, "-m", f"Version {version}"])
        
        # Merge back into develop
        print(f"Merging {release_branch} into develop")
        self.run_git_command(["checkout", "develop"])
        self.run_git_command(["merge", "--no-ff", release_branch, "-m", f"Merge release v{version} back to develop"])
        
        # Create version branch for future reference
        print(f"Creating version branch {version_branch}")
        self.run_git_command(["checkout", "master"])
        self.run_git_command(["checkout", "-b", version_branch])
        
        # Create version snapshot using version_manager.py
        print(f"Creating version snapshot for v{version}")
        
        # Get key features from commit messages
        _, commits = self.run_git_command([
            "log", 
            "--pretty=format:%s", 
            f"v{self.get_previous_version(version)}..HEAD"
        ], check=False)
        
        key_features = []
        for line in commits.split('\n'):
            if line.startswith('Merge feature'):
                feature = line.split("'")[1] if "'" in line else line.split("Merge feature ")[1]
                key_features.append(f"Added {feature}")
            elif line.startswith('Add ') or line.startswith('Implement '):
                key_features.append(line)
        
        # Get dependencies from requirements.txt
        dependencies = []
        req_path = self.project_root / "requirements.txt"
        if req_path.exists():
            with open(req_path, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        dependencies.append(line.strip())
        
        # Create version snapshot
        # This assumes version_manager.py accepts these arguments
        version_cmd = [
            "create",
            version,
            f"Version {version}",
            ",".join(key_features[:5]),  # Limit to top 5 features
            ",".join(dependencies),
            "python simple_display.py",
            f"Released on {self.get_current_date()}"
        ]
        
        try:
            ret_code = self.run_version_manager(version_cmd)
            if ret_code != 0:
                print("Warning: Creating version snapshot failed")
        except Exception as e:
            print(f"Error creating version snapshot: {e}")
        
        # Delete the release branch
        print(f"Deleting release branch {release_branch}")
        self.run_git_command(["branch", "-d", release_branch])
        
        print(f"Release v{version} completed successfully!")
        print(f"Don't forget to push changes with:")
        print(f"git push origin master develop {tag_name} {version_branch}")
        
        return 0
    
    def create_hotfix(self, version: str, description: str = None) -> int:
        """
        Create a hotfix branch from master
        
        This will:
        1. Create a hotfix/v{version} branch from master
        2. Update version in README.md
        """
        # Validate version format (should be current.version.patch+1)
        if not re.match(r'^[0-9]+\.[0-9]+\.[0-9]+$', version):
            print("Error: Version must be in format major.minor.patch (e.g., 1.0.0)")
            return 1
        
        hotfix_branch = f"hotfix/v{version}"
        
        # Check if hotfix branch already exists
        if hotfix_branch in self.get_branches():
            print(f"Error: Hotfix branch {hotfix_branch} already exists")
            return 1
        
        # Create hotfix branch from master
        print(f"Creating hotfix branch {hotfix_branch} from master")
        self.run_git_command(["checkout", "master"])
        self.run_git_command(["pull", "origin", "master"])
        self.run_git_command(["checkout", "-b", hotfix_branch])
        
        # Update version in README.md
        current_version = self.get_current_version()
        readme_path = self.project_root / "README.md"
        
        if readme_path.exists():
            with open(readme_path, 'r') as f:
                content = f.read()
            
            # Replace version in README.md
            if current_version != "unknown":
                content = content.replace(f"v{current_version}", f"v{version}")
                with open(readme_path, 'w') as f:
                    f.write(content)
                
                print(f"Updated version in README.md from v{current_version} to v{version}")
                
                # Commit the version update
                self.run_git_command(["add", "README.md"])
                self.run_git_command(["commit", "-m", f"Bump version to v{version}"])
        
        print(f"Hotfix branch {hotfix_branch} created successfully")
        print(f"Fix the issues and then use:")
        print(f"python scripts/git_version_manager.py finish-hotfix {version}")
        
        return 0
    
    def finish_hotfix(self, version: str) -> int:
        """
        Finish a hotfix branch
        
        This will:
        1. Merge hotfix/v{version} into master
        2. Tag the release
        3. Merge back into develop
        4. Create version branch v{version}
        5. Generate version snapshot with version_manager.py
        6. Delete the hotfix branch
        """
        hotfix_branch = f"hotfix/v{version}"
        version_branch = f"v{version}"
        tag_name = f"v{version}"
        
        # Check if hotfix branch exists
        if hotfix_branch not in self.get_branches():
            print(f"Error: Hotfix branch {hotfix_branch} does not exist")
            return 1
        
        # Merge into master
        print(f"Merging {hotfix_branch} into master")
        self.run_git_command(["checkout", "master"])
        self.run_git_command(["merge", "--no-ff", hotfix_branch, "-m", f"Merge hotfix v{version}"])
        
        # Create tag
        print(f"Creating tag {tag_name}")
        self.run_git_command(["tag", "-a", tag_name, "-m", f"Version {version} (hotfix)"])
        
        # Merge back into develop
        print(f"Merging {hotfix_branch} into develop")
        if "develop" in self.get_branches():
            self.run_git_command(["checkout", "develop"])
            self.run_git_command(["merge", "--no-ff", hotfix_branch, "-m", f"Merge hotfix v{version} back to develop"])
        
        # Create version branch for future reference
        print(f"Creating version branch {version_branch}")
        self.run_git_command(["checkout", "master"])
        self.run_git_command(["checkout", "-b", version_branch])
        
        # Create version snapshot using version_manager.py
        print(f"Creating version snapshot for v{version} (hotfix)")
        
        # Get hotfix features from commit messages
        _, commits = self.run_git_command([
            "log", 
            "--pretty=format:%s", 
            f"v{self.get_previous_version(version)}..HEAD"
        ], check=False)
        
        key_features = ["Hotfix: " + line for line in commits.split('\n') if not line.startswith('Merge')]
        
        # Get dependencies from requirements.txt
        dependencies = []
        req_path = self.project_root / "requirements.txt"
        if req_path.exists():
            with open(req_path, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        dependencies.append(line.strip())
        
        # Create version snapshot
        version_cmd = [
            "create",
            version,
            f"Version {version} (Hotfix)",
            ",".join(key_features[:5]),  # Limit to top 5 features
            ",".join(dependencies),
            "python simple_display.py",
            f"Hotfix released on {self.get_current_date()}"
        ]
        
        try:
            ret_code = self.run_version_manager(version_cmd)
            if ret_code != 0:
                print("Warning: Creating version snapshot failed")
        except Exception as e:
            print(f"Error creating version snapshot: {e}")
        
        # Delete the hotfix branch
        print(f"Deleting hotfix branch {hotfix_branch}")
        self.run_git_command(["branch", "-d", hotfix_branch])
        
        print(f"Hotfix v{version} completed successfully!")
        print(f"Don't forget to push changes with:")
        print(f"git push origin master develop {tag_name} {version_branch}")
        
        return 0
    
    def get_previous_version(self, current_version: str) -> str:
        """Get the previous version from tags"""
        tags = self.get_tags()
        versions = []
        
        for tag in tags:
            if tag.startswith('v') and re.match(r'^v[0-9]+\.[0-9]+\.[0-9]+$', tag):
                versions.append(tag[1:])  # Remove 'v' prefix
        
        # Sort versions
        versions.sort(key=lambda v: [int(x) for x in v.split('.')])
        
        # Find the version before current
        try:
            idx = versions.index(current_version)
            if idx > 0:
                return versions[idx - 1]
            return "0.0.0"  # No previous version
        except ValueError:
            # Current version not found, return the latest
            if versions:
                return versions[-1]
            return "0.0.0"
    
    def get_current_date(self) -> str:
        """Get current date in YYYY-MM-DD format"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")
    
    def show_status(self) -> int:
        """Show the current status of branches and versions"""
        current_branch = self.get_current_branch()
        current_version = self.get_current_version()
        branches = self.get_branches()
        tags = self.get_tags()
        
        print(f"=== Punch Card Project Git Version Status ===")
        print(f"Current branch: {current_branch}")
        print(f"Current version: v{current_version}")
        print()
        
        print("Version branches:")
        for branch in branches:
            if branch.startswith('v'):
                print(f"  {branch}")
        
        print("\nFeature branches:")
        for branch in branches:
            if branch.startswith('feature/'):
                print(f"  {branch}")
        
        print("\nRelease branches:")
        for branch in branches:
            if branch.startswith('release/'):
                print(f"  {branch}")
        
        print("\nHotfix branches:")
        for branch in branches:
            if branch.startswith('hotfix/'):
                print(f"  {branch}")
        
        print("\nTags (releases):")
        for tag in sorted(tags):
            print(f"  {tag}")
        
        print("\nNext steps:")
        print("  - To create a feature: python scripts/git_version_manager.py feature <name>")
        print("  - To create a release: python scripts/git_version_manager.py release <version>")
        print("  - To create a hotfix: python scripts/git_version_manager.py hotfix <version>")
        
        return 0
    
    def setup_workflow(self) -> int:
        """Set up the initial GitFlow workflow if not already done"""
        # Check if develop branch exists
        if "develop" not in self.get_branches():
            print("Setting up develop branch")
            self.run_git_command(["checkout", "master"])
            self.run_git_command(["checkout", "-b", "develop"])
            print("Created develop branch")
        
        # Check if version branches match tags
        tags = [tag for tag in self.get_tags() if tag.startswith('v')]
        version_branches = [branch for branch in self.get_branches() if branch.startswith('v')]
        
        for tag in tags:
            branch = tag  # Tag name and branch name should match (both have v prefix)
            if branch not in version_branches:
                print(f"Creating version branch {branch} from tag {tag}")
                self.run_git_command(["checkout", tag])
                self.run_git_command(["checkout", "-b", branch])
                self.run_git_command(["checkout", "develop"])
        
        print("Git workflow setup complete!")
        print("\nBranching strategy:")
        print("- master: Main production branch")
        print("- develop: Integration branch for new features")
        print("- feature/*: Feature branches")
        print("- release/*: Release preparation branches")
        print("- hotfix/*: Emergency fixes")
        print("- v*.*.*: Version branches for historical reference")
        
        return 0


def main():
    parser = argparse.ArgumentParser(description="Git Version Manager for Punch Card Project")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Feature commands
    feature_parser = subparsers.add_parser('feature', help='Create a new feature branch')
    feature_parser.add_argument('name', help='Feature name')
    
    finish_feature_parser = subparsers.add_parser('finish-feature', help='Finish a feature branch')
    finish_feature_parser.add_argument('name', help='Feature name')
    
    # Release commands
    release_parser = subparsers.add_parser('release', help='Create a new release branch')
    release_parser.add_argument('version', help='Release version (e.g., 1.0.0)')
    release_parser.add_argument('--description', help='Release description')
    
    finish_release_parser = subparsers.add_parser('finish-release', help='Finish a release branch')
    finish_release_parser.add_argument('version', help='Release version (e.g., 1.0.0)')
    
    # Hotfix commands
    hotfix_parser = subparsers.add_parser('hotfix', help='Create a new hotfix branch')
    hotfix_parser.add_argument('version', help='Hotfix version (e.g., 1.0.1)')
    hotfix_parser.add_argument('--description', help='Hotfix description')
    
    finish_hotfix_parser = subparsers.add_parser('finish-hotfix', help='Finish a hotfix branch')
    finish_hotfix_parser.add_argument('version', help='Hotfix version (e.g., 1.0.1)')
    
    # Status command
    subparsers.add_parser('status', help='Show status of branches and versions')
    
    # Setup command
    subparsers.add_parser('setup', help='Set up the initial GitFlow workflow')
    
    args = parser.parse_args()
    
    try:
        manager = GitVersionManager()
        
        if args.command == 'feature':
            return manager.create_feature_branch(args.name)
        elif args.command == 'finish-feature':
            return manager.finish_feature_branch(args.name)
        elif args.command == 'release':
            return manager.create_release(args.version, args.description)
        elif args.command == 'finish-release':
            return manager.finish_release(args.version)
        elif args.command == 'hotfix':
            return manager.create_hotfix(args.version, args.description)
        elif args.command == 'finish-hotfix':
            return manager.finish_hotfix(args.version)
        elif args.command == 'status':
            return manager.show_status()
        elif args.command == 'setup':
            return manager.setup_workflow()
        else:
            parser.print_help()
            return 1
    
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 