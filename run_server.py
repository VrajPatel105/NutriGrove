"""
Quick Start Script for NutriGrove WhatsApp Nutrition Coach

This script starts the FastAPI server with all services initialized.
"""

import uvicorn
import sys
import os

def main():
    """Start the server"""
    print("="*60)
    print("🍽️  NutriGrove WhatsApp Nutrition Coach")
    print("="*60)
    print("\nStarting server...")
    print("Dashboard: http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    print("WhatsApp Webhook: http://localhost:8000/whatsapp-webhook")
    print("\n" + "="*60)
    print("Press CTRL+C to stop")
    print("="*60 + "\n")

    # Check if .env exists
    if not os.path.exists('.env'):
        print("⚠️  WARNING: .env file not found!")
        print("Please copy .env.example to .env and fill in your API keys")
        print("\nRun: cp .env.example .env")
        sys.exit(1)

    # Start server
    uvicorn.run(
        "backend.app.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
