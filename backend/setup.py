"""Setup script for backend"""
import subprocess
import sys


def install_dependencies():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("Dependencies installed successfully!")


if __name__ == "__main__":
    install_dependencies()
