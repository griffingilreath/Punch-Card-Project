#!/bin/bash

# GitHub Synchronization Script for Punch Card Project
# This script helps synchronize local changes with the GitHub repository
# Usage: ./scripts/sync_github.sh [options]

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
VERSION="0.1.1"
COMMIT_MSG="Version ${VERSION}: Terminal Display Improvements"
PUSH_CHANGES=false
CREATE_TAG=false
FETCH_FIRST=true
FORCE_PUSH=false

# Display usage information
usage() {
    echo -e "${BLUE}GitHub Synchronization Script for Punch Card Project${NC}"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -m, --message MESSAGE   Specify commit message (default: '${COMMIT_MSG}')"
    echo "  -v, --version VERSION   Specify version for tag (default: ${VERSION})"
    echo "  -p, --push              Push changes to GitHub"
    echo "  -t, --tag               Create a version tag"
    echo "  -f, --force             Force push (use with caution!)"
    echo "  -n, --no-fetch          Skip fetching latest changes"
    echo "  -h, --help              Display this help message"
    echo ""
    exit 1
}

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--message)
            COMMIT_MSG="$2"
            shift 2
            ;;
        -v|--version)
            VERSION="$2"
            COMMIT_MSG="Version ${VERSION}: Terminal Display Improvements"
            shift 2
            ;;
        -p|--push)
            PUSH_CHANGES=true
            shift
            ;;
        -t|--tag)
            CREATE_TAG=true
            shift
            ;;
        -f|--force)
            FORCE_PUSH=true
            shift
            ;;
        -n|--no-fetch)
            FETCH_FIRST=false
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo -e "${RED}Error: Unknown option $1${NC}"
            usage
            ;;
    esac
done

# Navigate to the project root
cd "$(dirname "$0")/.." || { echo -e "${RED}Error: Could not navigate to project root${NC}"; exit 1; }

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo -e "${RED}Error: Not a git repository. Please run this script from the project root.${NC}"
    exit 1
fi

# Check git status
echo -e "${BLUE}Checking git status...${NC}"
git status

# Fetch latest changes if specified
if [ "$FETCH_FIRST" = true ]; then
    echo -e "\n${BLUE}Fetching latest changes from remote...${NC}"
    git fetch
    
    # Check if local branch is behind remote
    BEHIND=$(git rev-list HEAD..origin/main --count 2>/dev/null)
    if [ "$BEHIND" -gt 0 ]; then
        echo -e "${YELLOW}Warning: Your local branch is behind the remote by $BEHIND commit(s).${NC}"
        echo -e "You may want to pull changes before pushing: ${GREEN}git pull origin main${NC}"
        
        read -p "Would you like to pull changes now? (y/n): " PULL_CHANGES
        if [[ $PULL_CHANGES =~ ^[Yy]$ ]]; then
            echo -e "\n${BLUE}Pulling latest changes...${NC}"
            git pull origin main
            
            # Check for merge conflicts
            if [ $? -ne 0 ]; then
                echo -e "${RED}Error: Merge conflicts detected. Please resolve them before continuing.${NC}"
                exit 1
            fi
        fi
    fi
fi

# Check for unstaged changes
UNSTAGED=$(git status --porcelain | grep -v '??')
if [ -n "$UNSTAGED" ]; then
    echo -e "\n${BLUE}Unstaged changes detected. Would you like to stage them all?${NC}"
    git status --short
    read -p "Stage all changes? (y/n): " STAGE_ALL
    
    if [[ $STAGE_ALL =~ ^[Yy]$ ]]; then
        echo -e "\n${BLUE}Staging all changes...${NC}"
        git add .
    else
        echo -e "\n${BLUE}Please stage your changes manually and run this script again.${NC}"
        exit 0
    fi
fi

# Commit changes
echo -e "\n${BLUE}Committing changes with message:${NC} $COMMIT_MSG"
git commit -m "$COMMIT_MSG"

# Create tag if specified
if [ "$CREATE_TAG" = true ]; then
    echo -e "\n${BLUE}Creating tag v$VERSION...${NC}"
    git tag -a "v$VERSION" -m "Version $VERSION"
fi

# Push changes if specified
if [ "$PUSH_CHANGES" = true ]; then
    PUSH_CMD="git push origin main"
    
    # Add tag push if needed
    if [ "$CREATE_TAG" = true ]; then
        PUSH_CMD+=" && git push origin v$VERSION"
    fi
    
    # Add force flag if specified
    if [ "$FORCE_PUSH" = true ]; then
        PUSH_CMD="git push -f origin main"
        if [ "$CREATE_TAG" = true ]; then
            PUSH_CMD+=" && git push -f origin v$VERSION"
        fi
        echo -e "\n${YELLOW}Warning: Forcing push to remote!${NC}"
    fi
    
    echo -e "\n${BLUE}Pushing changes to GitHub...${NC}"
    echo -e "Running: ${GREEN}$PUSH_CMD${NC}"
    eval "$PUSH_CMD"
    
    if [ $? -eq 0 ]; then
        echo -e "\n${GREEN}Successfully synchronized with GitHub!${NC}"
    else
        echo -e "\n${RED}Failed to push to GitHub. Please check the error message above.${NC}"
    fi
else
    echo -e "\n${YELLOW}Changes have been committed locally but not pushed to GitHub.${NC}"
    echo -e "To push your changes, run: ${GREEN}git push origin main${NC}"
    if [ "$CREATE_TAG" = true ]; then
        echo -e "To push the new tag, run: ${GREEN}git push origin v$VERSION${NC}"
    fi
fi

# Show summary
echo -e "\n${BLUE}Summary:${NC}"
echo -e "  Version: ${GREEN}$VERSION${NC}"
echo -e "  Commit Message: ${GREEN}$COMMIT_MSG${NC}"
if [ "$CREATE_TAG" = true ]; then
    echo -e "  Tag Created: ${GREEN}v$VERSION${NC}"
fi
if [ "$PUSH_CHANGES" = true ]; then
    echo -e "  Changes Pushed: ${GREEN}Yes${NC}"
else
    echo -e "  Changes Pushed: ${YELLOW}No${NC}"
fi

# Final instructions
echo -e "\n${BLUE}Next Steps:${NC}"
if [ "$PUSH_CHANGES" = false ]; then
    echo -e "  - Push your changes to GitHub with: ${GREEN}git push origin main${NC}"
    if [ "$CREATE_TAG" = true ]; then
        echo -e "  - Push the tag with: ${GREEN}git push origin v$VERSION${NC}"
    fi
fi
echo -e "  - Update GitHub releases page with version notes"
echo -e "  - Notify team members about the update"
echo -e "\n${GREEN}Done!${NC}" 