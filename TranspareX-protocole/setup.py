#!/usr/bin/env python3
"""
TranspareX Setup Script
This script helps set up the TranspareX application
"""

import os
import sys
import subprocess

def install_requirements():
    """Install Python requirements"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = ".env"
    if not os.path.exists(env_file):
        print("📝 Creating .env file...")
        env_content = """# Database Configuration
DATABASE_URL=sqlite:///transparex.db

# Flask Configuration
SECRET_KEY=dev-secret-key-change-in-production
FLASK_ENV=development

# Blockchain Configuration
GANACHE_URL=http://127.0.0.1:7545
CONTRACT_ADDRESS=0x9b64DE133BAb117b4F37cf7fE239BF5e4C062aeD

# JWT Configuration
JWT_SECRET_KEY=jwt-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRES=3600
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ .env file created!")
    else:
        print("✅ .env file already exists!")

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is compatible!")
    return True

def main():
    """Main setup function"""
    print("🚀 TranspareX Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start Ganache (if using blockchain features)")
    print("2. Run: python run.py")
    print("3. Open: http://localhost:5000")
    print("4. Login with: admin@transparex.com / admin123")
    print("\n🔗 For more information, see README.md")

if __name__ == "__main__":
    main()
