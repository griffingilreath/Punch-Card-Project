"""
Web API Client for Punch Card Display System - Example Implementation

This module provides a client for sending statistics and system status
to the web API for remote monitoring.
"""

import requests
import json
import time
import threading
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

class PunchCardWebAPI:
    """Client for the Punch Card Display System web API."""
    
    def __init__(self, 
                 base_url: str = "https://api.punchcardproject.com",
                 api_key: Optional[str] = None,
                 auto_sync: bool = True,
                 sync_interval: int = 300):  # 5 minutes
        """Initialize the web API client.
        
        Args:
            base_url: Base URL for the API
            api_key: API key for authentication
            auto_sync: Whether to automatically sync statistics periodically
            sync_interval: Interval between automatic syncs (in seconds)
        """
        self.base_url = base_url
        self.api_key = api_key
        self.auto_sync = auto_sync
        self.sync_interval = sync_interval
        self.sync_thread = None
        self.last_sync = 0
        
        # Start auto-sync thread if enabled
        if self.auto_sync:
            self._start_sync_thread()
    
    def _start_sync_thread(self) -> None:
        """Start the background thread for automatic syncing."""
        def sync_worker():
            while self.auto_sync:
                current_time = time.time()
                if current_time - self.last_sync >= self.sync_interval:
                    try:
                        self.sync_statistics()
                        self.last_sync = current_time
                    except Exception as e:
                        print(f"Auto-sync error: {e}")
                time.sleep(10)  # Check every 10 seconds
        
        self.sync_thread = threading.Thread(target=sync_worker, daemon=True)
        self.sync_thread.start()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "PunchCardClient/1.0"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        return headers
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get the current system status from the API."""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/status",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting system status: {e}")
            return {"error": str(e)}
    
    def sync_statistics(self, stats: Optional[Dict[str, Any]] = None) -> bool:
        """Sync statistics to the web API.
        
        Args:
            stats: Statistics to sync (if None, collects current statistics)
            
        Returns:
            True if successful, False otherwise
        """
        if stats is None:
            stats = self._collect_current_statistics()
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/statistics",
                headers=self._get_headers(),
                json=stats
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error syncing statistics: {e}")
            return False
    
    def _collect_current_statistics(self) -> Dict[str, Any]:
        """Collect current statistics from the system."""
        # This would integrate with your punch card stats system
        # For example, reading from punch_card_stats.json
        
        try:
            # Find stats file relative to project root
            project_root = Path(__file__).parent
            stats_path = project_root / "punch_card_stats.json"
            
            with open(stats_path, "r") as f:
                stats = json.load(f)
            
            # Add timestamp and client information
            stats["timestamp"] = datetime.now().isoformat()
            stats["client_version"] = "1.0.0"
            
            return stats
        except Exception as e:
            print(f"Error collecting statistics: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "client_version": "1.0.0"
            }
    
    def get_message_history(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Get message history from the API.
        
        Args:
            limit: Maximum number of messages to retrieve
            offset: Offset for pagination
            
        Returns:
            Message history data
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/messages",
                headers=self._get_headers(),
                params={"limit": limit, "offset": offset}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting message history: {e}")
            return {"error": str(e), "messages": []}
    
    def shutdown(self) -> None:
        """Shutdown the web API client."""
        self.auto_sync = False
        if self.sync_thread and self.sync_thread.is_alive():
            self.sync_thread.join(timeout=1.0)


# Example usage
def main():
    """Example of using the web API client."""
    # Create the client
    api_client = PunchCardWebAPI(
        base_url="https://api.punchcardproject.com",
        api_key="your-api-key-here",
        auto_sync=True,
        sync_interval=60  # For demonstration, sync every minute
    )
    
    try:
        # Manually sync statistics once
        success = api_client.sync_statistics()
        print(f"Manual sync {'successful' if success else 'failed'}")
        
        # Get system status
        status = api_client.get_system_status()
        print(f"System status: {status}")
        
        # Get message history
        history = api_client.get_message_history(limit=10)
        print(f"Recent messages: {len(history.get('messages', []))}")
        
        # Let auto-sync run for a while
        print("Auto-sync running. Press Ctrl+C to exit...")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        # Clean shutdown
        api_client.shutdown()


if __name__ == "__main__":
    main() 