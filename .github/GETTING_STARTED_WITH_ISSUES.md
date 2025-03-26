# Getting Started with GitHub Issues

This guide will help you understand how to use GitHub issues to manage your Punch Card Project development workflow.

## What are GitHub Issues?

GitHub Issues are a way to track bugs, feature requests, and other tasks related to your project. They provide a structured way to organize work, track progress, and collaborate with others.

## How to Create a New Issue

1. Go to your GitHub repository (https://github.com/griffingilreath/Punch-Card-Project)
2. Click on the "Issues" tab near the top of the page
3. Click the green "New issue" button
4. Choose an issue template (bug report, feature request, or one of the specific issues)
5. Fill in the details and click "Submit new issue"

## Working with Issues

When you start working on an issue, here's a recommended workflow:

1. **Assign the issue to yourself** - Click "assign yourself" on the right sidebar
2. **Create a new branch** - Use the branch naming convention: `issue-[NUMBER]-[SHORT-DESCRIPTION]`
   ```bash
   git checkout -b issue-1-hardware-integration
   ```
3. **Make your changes** - Work on the code needed to resolve the issue
4. **Commit regularly** - Make frequent, small commits with clear messages
   ```bash
   git add .
   git commit -m "Add hardware controller module with basic connection functionality #1"
   ```
   (The `#1` at the end references issue number 1)
5. **Push your changes** to GitHub
   ```bash
   git push origin issue-1-hardware-integration
   ```
6. **Create a Pull Request** when you're ready for your changes to be merged
   - Go to the repository on GitHub
   - Click "Pull requests" tab
   - Click "New pull request"
   - Select your branch and fill in details
   - Reference the issue with "Fixes #1" in the description

7. **Close the issue** - When the PR is merged, you can close the issue (or GitHub will automatically close it if you used "Fixes #X" in your PR)

## Issue Workflow Example

Here's an example of working on the "Implement Physical LED Grid Controller" issue:

1. Assign the issue to yourself
2. Create a new branch: `git checkout -b issue-1-led-controller`
3. Study the existing code in `src/display/gui_display.py` and `docs/technical/NEOPIXEL_INTEGRATION.md`
4. Create a new module for hardware control
5. Implement the communication protocol
6. Test the implementation
7. Commit your changes: `git commit -m "Implement LED grid controller for Raspberry Pi #1"`
8. Push to GitHub: `git push origin issue-1-led-controller`
9. Create a PR, referencing "Fixes #1" in the description
10. Once reviewed and merged, the issue will be closed

## Best Practices

- **One issue, one task** - Keep issues focused on a single task or feature
- **Reference issues in commits** - Use `#1` in commit messages to link to the issue
- **Keep issues updated** - Add comments about your progress
- **Use labels** - They help categorize and prioritize issues
- **Close resolved issues** - When work is complete, close the issue

Happy coding! 