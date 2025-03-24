
## Security Note

**Important**: Any API keys that might appear in the repository history are no longer valid and have been rotated.
This project uses a secure approach for handling API keys:

1. API keys are stored in a 'secrets' directory that is excluded from Git
2. The .gitignore file explicitly excludes backup files that might contain sensitive information
3. We use environment variables as the preferred method for storing API keys
4. The dedicated 'update_api_key.py' utility helps securely manage API keys

To set up your API key:
1. Run 'python update_api_key.py' and follow the prompts
2. Or set the 'OPENAI_API_KEY' environment variable

Never commit API keys or other secrets directly to the repository.
