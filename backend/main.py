"""
Main entry point for production deployment.
Imports the FastAPI app from app.main for compatibility with deployment platforms.
"""

from app.main import app

# This allows Render and other platforms to use: uvicorn main:app
# while maintaining the clean app/ directory structure

if __name__ == "__main__":
    import uvicorn
    import os

    # Get port from environment (Render uses $PORT)
    port = int(os.getenv("PORT", 8000))

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
