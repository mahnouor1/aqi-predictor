#!/usr/bin/env python3
"""
Hourly trigger script for AQI Predictor
This script can be run by external services to trigger deployments
"""

import requests
import json
import os
from datetime import datetime

def trigger_github_workflow():
    """Trigger GitHub workflow using repository dispatch"""
    
    # GitHub repository info
    repo_owner = "mahnouor1"
    repo_name = "aqi-predictor"
    
    # GitHub token (you'll need to set this as an environment variable)
    github_token = os.getenv('GITHUB_TOKEN')
    
    if not github_token:
        print("❌ GITHUB_TOKEN environment variable not set")
        return False
    
    # GitHub API endpoint
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/dispatches"
    
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    payload = {
        "event_type": "hourly-trigger",
        "client_payload": {
            "timestamp": datetime.now().isoformat(),
            "trigger": "hourly-schedule"
        }
    }
    
    try:
        print(f"🔄 Triggering hourly deployment at {datetime.now()}")
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 204:
            print("✅ Hourly deployment triggered successfully!")
            return True
        else:
            print(f"❌ Failed to trigger deployment: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error triggering deployment: {e}")
        return False

def main():
    """Main function"""
    print("🚀 AQI Predictor Hourly Trigger")
    print(f"⏰ Time: {datetime.now()}")
    
    success = trigger_github_workflow()
    
    if success:
        print("🎉 Hourly deployment initiated!")
    else:
        print("💥 Failed to trigger hourly deployment")
    
    return success

if __name__ == "__main__":
    main()
