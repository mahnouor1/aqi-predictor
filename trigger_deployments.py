#!/usr/bin/env python3
"""
Trigger Multiple Deployments
This script will create multiple commits to trigger deployments
"""

import os
import subprocess
import time
from datetime import datetime

def create_deployment_commit():
    """Create a deployment commit"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create a small change to trigger deployment
    with open("deployment_log.txt", "a") as f:
        f.write(f"Deployment triggered at {timestamp}\n")
    
    # Add and commit
    subprocess.run(["git", "add", "deployment_log.txt"])
    subprocess.run(["git", "commit", "-m", f"🚀 Trigger deployment #{timestamp}"])
    subprocess.run(["git", "push", "origin", "main"])
    
    print(f"✅ Deployment #{timestamp} pushed!")

def main():
    """Trigger multiple deployments"""
    print("🚀 Triggering multiple deployments...")
    
    # Trigger 5 deployments with 30-second intervals
    for i in range(5):
        print(f"📦 Creating deployment {i+1}/5...")
        create_deployment_commit()
        
        if i < 4:  # Don't wait after the last one
            print("⏳ Waiting 30 seconds...")
            time.sleep(30)
    
    print("🎉 All deployments triggered!")

if __name__ == "__main__":
    main()
