#!/usr/bin/env python3
"""
Research Paper Generator - Main Application
Professional tool for generating research papers from GitHub repositories
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from src.web.app import app

def main():
    """Main entry point for the application"""
    # Check if Gemini API key is set
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ Error: GEMINI_API_KEY environment variable is not set")
        print("Please set your Gemini API key in the .env file or as an environment variable")
        print("Example: export GEMINI_API_KEY='your-api-key-here'")
        print("Get your API key from: https://makersuite.google.com/app/apikey")
        sys.exit(1)
    
    # Create necessary directories
    os.makedirs('generated_papers', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('src/templates', exist_ok=True)
    
    print("🚀 Starting Research Paper Generator...")
    port = int(os.getenv('PORT', '3000'))
    print(f"📝 Available at: http://localhost:{port}")
    print("🔑 Using Gemini AI for content generation")
    print("=" * 50)
    
    # Run the Flask application
    app.run(debug=False, use_reloader=False, host='0.0.0.0', port=port)

if __name__ == '__main__':
    main()
