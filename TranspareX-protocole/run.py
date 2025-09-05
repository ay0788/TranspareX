#!/usr/bin/env python3
"""
TranspareX Application Startup Script
Run this script to start the TranspareX application
"""

import os
import sys
from app import app

if __name__ == '__main__':
    # Set environment variables for development
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('FLASK_DEBUG', '1')
    
    print("🚀 Starting TranspareX Application...")
    print("📊 AI & Blockchain for Financial Transparency")
    print("🌐 Server will be available at: http://localhost:5000")
    print("👤 Default admin credentials: admin@transparex.com / admin123")
    print("=" * 60)
    
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 TranspareX application stopped.")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)
