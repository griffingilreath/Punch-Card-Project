#!/usr/bin/env python3
import os
import shutil
import json
import datetime
from typing import List, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class VersionInfo:
    version: str
    date: str
    description: str
    key_features: List[str]
    files_included: List[str]
    dependencies: List[str]
    run_instructions: List[str]
    notes: str

class VersionManager:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.versions_dir = self.project_root / "versions"
        self.src_dir = self.project_root / "src"
        self.data_dir = self.project_root / "data"
        self.config_dir = self.project_root / "config"
        self.tests_dir = self.project_root / "tests"
        
        # Ensure versions directory exists
        self.versions_dir.mkdir(exist_ok=True)
        
    def create_version(self, version: str, description: str, key_features: List[str], 
                      dependencies: List[str], run_instructions: List[str], notes: str = "") -> None:
        """Create a new version of the project"""
        version_dir = self.versions_dir / version
        
        # Create version directory structure
        for subdir in ['src', 'data', 'config', 'tests']:
            (version_dir / subdir).mkdir(parents=True, exist_ok=True)
        
        # Copy source files
        if self.src_dir.exists():
            for item in self.src_dir.glob('*'):
                if item.is_file() and not item.name.startswith('.'):
                    shutil.copy2(item, version_dir / 'src')
        
        # Copy data files
        if self.data_dir.exists():
            for item in self.data_dir.glob('*'):
                if item.is_file() and not item.name.startswith('.'):
                    shutil.copy2(item, version_dir / 'data')
        
        # Copy config files
        if self.config_dir.exists():
            for item in self.config_dir.glob('*'):
                if item.is_file() and not item.name.startswith('.'):
                    shutil.copy2(item, version_dir / 'config')
        
        # Copy test files
        if self.tests_dir.exists():
            for item in self.tests_dir.glob('*'):
                if item.is_file() and not item.name.startswith('.'):
                    shutil.copy2(item, version_dir / 'tests')
        
        # Copy project files
        for file in ['requirements.txt', 'README.md']:
            if (self.project_root / file).exists():
                shutil.copy2(self.project_root / file, version_dir)
        
        # Create version info file
        version_info = VersionInfo(
            version=version,
            date=datetime.datetime.now().strftime("%Y-%m-%d"),
            description=description,
            key_features=key_features,
            files_included=self._get_files_list(version_dir),
            dependencies=dependencies,
            run_instructions=run_instructions,
            notes=notes
        )
        
        self._write_version_info(version_dir, version_info)
        
        # Set proper permissions
        self._set_permissions(version_dir)
        
    def list_versions(self) -> List[str]:
        """List all available versions"""
        return [d.name for d in self.versions_dir.iterdir() if d.is_dir()]
    
    def restore_version(self, version: str) -> None:
        """Restore a specific version"""
        version_dir = self.versions_dir / version
        if not version_dir.exists():
            raise ValueError(f"Version {version} does not exist")
        
        # Restore source files
        if (version_dir / 'src').exists():
            shutil.rmtree(self.src_dir, ignore_errors=True)
            shutil.copytree(version_dir / 'src', self.src_dir)
        
        # Restore data files
        if (version_dir / 'data').exists():
            shutil.rmtree(self.data_dir, ignore_errors=True)
            shutil.copytree(version_dir / 'data', self.data_dir)
        
        # Restore config files
        if (version_dir / 'config').exists():
            shutil.rmtree(self.config_dir, ignore_errors=True)
            shutil.copytree(version_dir / 'config', self.config_dir)
        
        # Restore test files
        if (version_dir / 'tests').exists():
            shutil.rmtree(self.tests_dir, ignore_errors=True)
            shutil.copytree(version_dir / 'tests', self.tests_dir)
        
        # Restore project files
        for file in ['requirements.txt', 'README.md']:
            if (version_dir / file).exists():
                shutil.copy2(version_dir / file, self.project_root)
    
    def get_version_info(self, version: str) -> Optional[VersionInfo]:
        """Get information about a specific version"""
        version_dir = self.versions_dir / version
        if not version_dir.exists():
            return None
        
        info_file = version_dir / 'version_info.txt'
        if not info_file.exists():
            return None
        
        return self._read_version_info(info_file)
    
    def _get_files_list(self, directory: Path) -> List[str]:
        """Get a list of all files in the version directory"""
        files = []
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                if not filename.startswith('.'):
                    rel_path = Path(root).relative_to(directory)
                    files.append(str(rel_path / filename))
        return sorted(files)
    
    def _write_version_info(self, version_dir: Path, info: VersionInfo) -> None:
        """Write version information to version_info.txt"""
        with open(version_dir / 'version_info.txt', 'w') as f:
            f.write(f"Version: {info.version}\n")
            f.write(f"Date: {info.date}\n")
            f.write(f"Description: {info.description}\n\n")
            
            f.write("Key Features:\n")
            for feature in info.key_features:
                f.write(f"- {feature}\n")
            f.write("\n")
            
            f.write("Files Included:\n")
            for file in info.files_included:
                f.write(f"- {file}\n")
            f.write("\n")
            
            f.write("Directory Structure:\n")
            f.write(f"/versions/{info.version}/\n")
            f.write("├── src/           # Source code files\n")
            f.write("├── data/          # Data files and databases\n")
            f.write("├── config/        # Configuration files\n")
            f.write("├── tests/         # Test files\n")
            f.write("├── requirements.txt\n")
            f.write("├── README.md\n")
            f.write("└── version_info.txt\n\n")
            
            f.write("Dependencies:\n")
            for dep in info.dependencies:
                f.write(f"- {dep}\n")
            f.write("\n")
            
            f.write("To Run:\n")
            for step in info.run_instructions:
                f.write(f"{step}\n")
            f.write("\n")
            
            if info.notes:
                f.write(f"Note: {info.notes}\n")
    
    def _read_version_info(self, info_file: Path) -> VersionInfo:
        """Read version information from version_info.txt"""
        with open(info_file, 'r') as f:
            lines = f.readlines()
        
        # Parse the file content
        version = lines[0].split(': ')[1].strip()
        date = lines[1].split(': ')[1].strip()
        description = lines[2].split(': ')[1].strip()
        
        # Parse key features
        key_features = []
        i = 4
        while i < len(lines) and lines[i].strip().startswith('-'):
            key_features.append(lines[i].strip()[2:])
            i += 1
        
        # Parse files included
        files_included = []
        i += 2
        while i < len(lines) and lines[i].strip().startswith('-'):
            files_included.append(lines[i].strip()[2:])
            i += 1
        
        # Parse dependencies
        dependencies = []
        i += 2
        while i < len(lines) and lines[i].strip().startswith('-'):
            dependencies.append(lines[i].strip()[2:])
            i += 1
        
        # Parse run instructions
        run_instructions = []
        i += 2
        while i < len(lines) and not lines[i].strip().startswith('Note:'):
            run_instructions.append(lines[i].strip())
            i += 1
        
        # Parse notes
        notes = lines[i].split(': ')[1].strip() if i < len(lines) else ""
        
        return VersionInfo(
            version=version,
            date=date,
            description=description,
            key_features=key_features,
            files_included=files_included,
            dependencies=dependencies,
            run_instructions=run_instructions,
            notes=notes
        )
    
    def _set_permissions(self, directory: Path) -> None:
        """Set proper permissions for all files and directories"""
        # Set directory permissions to 755
        for root, dirs, files in os.walk(directory):
            for d in dirs:
                os.chmod(Path(root) / d, 0o755)
            # Set file permissions to 644
            for f in files:
                os.chmod(Path(root) / f, 0o644)

def main():
    """Command-line interface for version management"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage project versions')
    parser.add_argument('action', choices=['create', 'list', 'restore', 'info'],
                      help='Action to perform')
    parser.add_argument('version', nargs='?', help='Version number (e.g., 0.1.0)')
    parser.add_argument('--description', help='Version description')
    parser.add_argument('--features', nargs='+', help='Key features')
    parser.add_argument('--dependencies', nargs='+', help='Dependencies')
    parser.add_argument('--instructions', nargs='+', help='Run instructions')
    parser.add_argument('--notes', help='Additional notes')
    
    args = parser.parse_args()
    
    # Get the project root directory (parent of this script)
    project_root = Path(__file__).parent
    manager = VersionManager(str(project_root))
    
    if args.action == 'create':
        if not all([args.version, args.description, args.features, 
                   args.dependencies, args.instructions]):
            print("Error: All arguments are required for version creation")
            return
        
        manager.create_version(
            version=args.version,
            description=args.description,
            key_features=args.features,
            dependencies=args.dependencies,
            run_instructions=args.instructions,
            notes=args.notes or ""
        )
        print(f"Created version {args.version}")
    
    elif args.action == 'list':
        versions = manager.list_versions()
        if versions:
            print("Available versions:")
            for version in versions:
                print(f"- {version}")
        else:
            print("No versions found")
    
    elif args.action == 'restore':
        if not args.version:
            print("Error: Version number is required")
            return
        
        try:
            manager.restore_version(args.version)
            print(f"Restored version {args.version}")
        except ValueError as e:
            print(f"Error: {e}")
    
    elif args.action == 'info':
        if not args.version:
            print("Error: Version number is required")
            return
        
        info = manager.get_version_info(args.version)
        if info:
            print(f"\nVersion: {info.version}")
            print(f"Date: {info.date}")
            print(f"Description: {info.description}")
            print("\nKey Features:")
            for feature in info.key_features:
                print(f"- {feature}")
            print("\nFiles Included:")
            for file in info.files_included:
                print(f"- {file}")
            print("\nDependencies:")
            for dep in info.dependencies:
                print(f"- {dep}")
            print("\nTo Run:")
            for step in info.run_instructions:
                print(step)
            if info.notes:
                print(f"\nNote: {info.notes}")
        else:
            print(f"Version {args.version} not found")

if __name__ == '__main__':
    main() 