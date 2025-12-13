#!/usr/bin/env python3
"""
Test Runner Script for CultureUp API Testing
Installs dependencies and runs tests
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages for testing"""
    print("📦 Installing test dependencies...")
    
    required_packages = [
        'requests',
        'Pillow'
    ]
    
    for package in required_packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} installed")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False
    
    return True

def check_django_server():
    """Check if Django server is running"""
    import requests
    try:
        response = requests.get("http://127.0.0.1:8000/api/", timeout=5)
        return True
    except:
        return False

def start_django_server():
    """Instructions to start Django server"""
    print("\n🚀 Django Server Setup:")
    print("1. Open a new terminal/command prompt")
    print("2. Navigate to your project directory")
    print("3. Run: python manage.py runserver")
    print("4. Wait for server to start")
    print("5. Come back and run this test again")

def main():
    """Main function"""
    print("🧪 CultureUp API Test Runner")
    print("=" * 40)
    
    # Install dependencies
    if not install_requirements():
        print("❌ Failed to install dependencies")
        return
    
    # Check if Django server is running
    if not check_django_server():
        print("⚠️  Django server is not running!")
        start_django_server()
        
        input("\nPress Enter when Django server is running...")
        
        if not check_django_server():
            print("❌ Still cannot connect to Django server")
            return
    
    print("✅ Django server is running!")
    
    # Run the simple test
    print("\n🧪 Running Simple HTTP API Tests...")
    try:
        import simple_api_test
        simple_api_test.main()
    except ImportError:
        print("❌ Cannot import simple_api_test.py")
        print("💡 Make sure simple_api_test.py is in the same directory")
    except Exception as e:
        print(f"❌ Error running tests: {str(e)}")

if __name__ == "__main__":
    main()