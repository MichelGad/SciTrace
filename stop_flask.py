#!/usr/bin/env python3
"""
Script to stop Flask app running on port 5001
"""
import subprocess
import sys

def stop_flask_on_port(port=5001):
    """Stop any process running on the specified port"""
    try:
        # Find process using the port
        result = subprocess.run(['lsof', '-ti', f':{port}'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid.strip():
                    print(f"Stopping process {pid} on port {port}...")
                    subprocess.run(['kill', pid.strip()])
                    print(f"Process {pid} stopped successfully")
        else:
            print(f"No process found running on port {port}")
            
    except Exception as e:
        print(f"Error stopping Flask app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    stop_flask_on_port()
