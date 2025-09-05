#!/usr/bin/env python3
"""
TranspareX Restart Script
This script restarts the application with updated configuration
"""

import os
import sys
import subprocess
import time

def restart_app():
    """Restart the TranspareX application"""
    print("🔄 Restarting TranspareX Application...")
    print("=" * 50)
    
    # Kill any existing Python processes running the app
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(['taskkill', '/f', '/im', 'python.exe'], 
                         capture_output=True, text=True)
        else:  # Unix/Linux/Mac
            subprocess.run(['pkill', '-f', 'run.py'], 
                         capture_output=True, text=True)
        time.sleep(2)
    except:
        pass
    
    print("✅ Previous instances stopped")
    print("🚀 Starting TranspareX with updated configuration...")
    
    # Start the application
    try:
        subprocess.run([sys.executable, 'run.py'])
    except KeyboardInterrupt:
        print("\n👋 TranspareX application stopped.")
    except Exception as e:
        print(f"❌ Error starting application: {e}")

if __name__ == "__main__":
    restart_app()
