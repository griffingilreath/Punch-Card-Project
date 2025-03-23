import random
import yaml
import os
from typing import Optional, Dict, List
from openai import OpenAI
from datetime import datetime

class MessageGenerator:
    def __init__(self, config_path: str = "../config/config.yaml", 
                 credentials_path: str = "../config/credentials.yaml"):
        """Initialize message generator with configuration and credentials"""
        self.config = self._load_config(config_path)
        self.credentials = self._load_credentials(credentials_path)
        self.openai_client = None
        self._setup_openai()
        
        # Initialize punch card specific word lists
        self._init_word_lists()
        
    def _init_word_lists(self):
        """Initialize word lists for punch card messages"""
        # Vintage computing terms
        self.vintage_terms = [
            "BATCH", "JOB", "TASK", "PROCESS", "QUEUE", "STACK", "BUFFER",
            "MEMORY", "STORAGE", "PROCESSOR", "COMPUTER", "SYSTEM", "PROGRAM",
            "ROUTINE", "SUBROUTINE", "FUNCTION", "MODULE", "COMPILE", "ASSEMBLE",
            "LOAD", "EXECUTE", "DEBUG", "TRACE", "DUMP", "CORE", "DISK", "TAPE",
            "CARD", "PUNCH", "READER", "PRINTER", "TERMINAL", "CONSOLE", "KEYPUNCH"
        ]
        
        # System status terms
        self.status_terms = [
            "READY", "RUNNING", "WAITING", "HALTED", "ERROR", "COMPLETE",
            "PROCESSING", "QUEUED", "SCHEDULED", "ABORTED", "TERMINATED",
            "INITIALIZED", "CONFIGURED", "LOADED", "EXECUTING", "PAUSED"
        ]
        
        # Diagnostic categories
        self.diagnostic_categories = [
            "CPU", "MEMORY", "STORAGE", "I/O", "NETWORK", "SYSTEM",
            "PROCESS", "JOB", "TASK", "USER", "SECURITY", "PERFORMANCE"
        ]
        
        # Diagnostic keys
        self.diagnostic_keys = [
            "USAGE", "STATUS", "LEVEL", "COUNT", "RATE", "SIZE",
            "TIME", "SPEED", "ERRORS", "WARNINGS", "ALERTS", "QUEUE"
        ]
        
        # Diagnostic values
        self.diagnostic_values = [
            "OK", "WARNING", "ERROR", "CRITICAL", "NORMAL", "HIGH",
            "LOW", "FULL", "EMPTY", "BUSY", "IDLE", "STANDBY"
        ]
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {
                'message_generation': {
                    'model': 'gpt-3.5-turbo',
                    'max_tokens': 50,
                    'temperature': 0.7
                }
            }
            
    def _load_credentials(self, credentials_path: str) -> Dict:
        """Load credentials from YAML file"""
        if os.path.exists(credentials_path):
            with open(credentials_path, 'r') as f:
                return yaml.safe_load(f)
        return {}
        
    def _setup_openai(self):
        """Setup OpenAI client if credentials are available"""
        if self.credentials.get('openai', {}).get('api_key'):
            self.openai_client = OpenAI(
                api_key=self.credentials['openai']['api_key'],
                organization=self.credentials['openai'].get('organization_id')
            )
            
    def generate_random_sentence(self) -> str:
        """Generate a random sentence with vintage computing terminology"""
        # Generate sentence components
        sentence_parts = []
        current_length = 0
        
        # 70% chance to start with a system status
        if random.random() < 0.7:
            status = random.choice(self.status_terms)
            sentence_parts.append(status)
            current_length = len(status)
            
            # Add "SYSTEM" or "JOB" (40% chance)
            if random.random() < 0.4:
                system = random.choice(["SYSTEM", "JOB", "TASK"])
                if current_length + len(system) + 1 <= 80:
                    sentence_parts.append(system)
                    current_length += len(system) + 1
        else:
            # Start with a vintage term
            term = random.choice(self.vintage_terms)
            sentence_parts.append(term)
            current_length = len(term)
        
        # Add verb (80% chance)
        if random.random() < 0.8:
            verbs = ["PROCESSING", "EXECUTING", "RUNNING", "COMPILING", "LOADING", "SAVING"]
            verb = random.choice(verbs)
            if current_length + len(verb) + 1 <= 80:
                sentence_parts.append(verb)
                current_length += len(verb) + 1
        
        # Add data or program name (60% chance)
        if random.random() < 0.6:
            data_types = ["DATA", "PROGRAM", "ROUTINE", "MODULE", "FILE", "RECORD"]
            data = random.choice(data_types)
            if current_length + len(data) + 1 <= 80:
                sentence_parts.append(data)
                current_length += len(data) + 1
        
        # Add number or percentage (40% chance)
        if random.random() < 0.4:
            if random.random() < 0.5:
                number = str(random.randint(1, 9999))
            else:
                number = f"{random.randint(0, 100)}%"
            if current_length + len(number) + 1 <= 80:
                sentence_parts.append(number)
                current_length += len(number) + 1
        
        # Add timestamp (30% chance)
        if random.random() < 0.3:
            timestamp = datetime.now().strftime("%H:%M:%S")
            if current_length + len(timestamp) + 1 <= 80:
                sentence_parts.append(timestamp)
                current_length += len(timestamp) + 1
        
        # Join parts with spaces and add period
        sentence = " ".join(sentence_parts) + "."
        
        # Ensure sentence doesn't exceed 80 characters
        return sentence[:80]
        
    def generate_openai_message(self) -> Optional[str]:
        """Generate a message using OpenAI API"""
        if not self.openai_client:
            return None
            
        try:
            response = self.openai_client.chat.completions.create(
                model=self.config['message_generation']['model'],
                messages=[
                    {"role": "system", "content": "Generate a short, punchy message (max 80 characters) that would be suitable for display on an IBM punch card. Use only uppercase letters, numbers, and basic punctuation. The message should be interesting but concise."},
                    {"role": "user", "content": "Generate a message for the punch card display."}
                ],
                max_tokens=self.config['message_generation']['max_tokens'],
                temperature=self.config['message_generation']['temperature']
            )
            
            message = response.choices[0].message.content.strip().upper()
            # Ensure message doesn't exceed 80 characters
            return message[:80]
            
        except Exception as e:
            print(f"Error generating OpenAI message: {e}")
            return None
            
    def generate_diagnostic_message(self, category: str = None, key: str = None, value: str = None) -> str:
        """Generate a formatted diagnostic message"""
        if not category:
            category = random.choice(self.diagnostic_categories)
        if not key:
            key = random.choice(self.diagnostic_keys)
        if not value:
            value = random.choice(self.diagnostic_values)
            
        # Add timestamp (30% chance)
        timestamp = ""
        if random.random() < 0.3:
            timestamp = f" [{datetime.now().strftime('%H:%M:%S')}]"
            
        message = f"DIAGNOSTIC {category}: {key}={value}{timestamp}"
        return message[:80]  # Ensure message doesn't exceed 80 characters
        
    def generate_system_message(self) -> str:
        """Generate a system status message"""
        status = random.choice(self.status_terms)
        system = random.choice(["SYSTEM", "JOB", "TASK"])
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = f"{status} {system} [{timestamp}]"
        return message[:80]  # Ensure message doesn't exceed 80 characters 