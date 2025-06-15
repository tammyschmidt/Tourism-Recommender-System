import subprocess
import sys
import os
import webbrowser
from threading import Thread
import time
import shutil

def get_npm_path():
    """Get the full path to npm executable"""
    npm_path = shutil.which('npm')
    if npm_path is None:
        # Try to find npm in common installation locations
        common_paths = [
            os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'nodejs', 'npm.cmd'),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'), 'nodejs', 'npm.cmd'),
            os.path.join(os.environ.get('APPDATA', ''), 'npm', 'npm.cmd'),
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path
        print("Error: npm is not installed or not in system PATH")
        print("Please install Node.js from: https://nodejs.org/")
        print("After installation, restart your terminal and try again.")
        sys.exit(1)
    return npm_path

def run_backend():
    """Run the FastAPI backend server"""
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
    os.chdir(backend_dir)
    subprocess.run([sys.executable, 'main.py'])

def run_frontend():
    """Run the Vite frontend development server"""
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')
    if not os.path.exists(frontend_dir):
        print(f"Error: Frontend directory not found at {frontend_dir}")
        print("Please make sure you have the frontend directory in the project root.")
        sys.exit(1)
    
    npm_path = get_npm_path()
    
    # Check if node_modules exists
    node_modules = os.path.join(frontend_dir, 'node_modules')
    if not os.path.exists(node_modules):
        print("Installing frontend dependencies...")
        os.chdir(frontend_dir)
        try:
            subprocess.run([npm_path, 'install'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies: {e}")
            sys.exit(1)
    
    os.chdir(frontend_dir)
    try:
        subprocess.run([npm_path, 'run', 'dev'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running frontend server: {e}")
        sys.exit(1)

def main():
    # Get the absolute path of the project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Check if backend directory exists
    backend_dir = os.path.join(project_root, 'backend')
    if not os.path.exists(backend_dir):
        print(f"Error: Backend directory not found at {backend_dir}")
        print("Please make sure you have the backend directory in the project root.")
        sys.exit(1)
    
    # Create threads for frontend and backend
    backend_thread = Thread(target=lambda: run_backend())
    frontend_thread = Thread(target=lambda: run_frontend())
    
    # Start both servers
    print("Starting backend server...")
    backend_thread.start()
    
    # Wait a bit for backend to start
    time.sleep(2)
    
    print("Starting frontend server...")
    frontend_thread.start()
    
    # Open the frontend in the default browser
    time.sleep(3)  # Wait for frontend to start
    webbrowser.open('http://localhost:5173')  # Default Vite dev server port
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        sys.exit(0)

if __name__ == "__main__":
    main() 