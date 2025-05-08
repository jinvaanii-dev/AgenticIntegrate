# Main entry point for the AgenticAI Integration Platform
# This file imports and uses the implementation from simple_server.py

# Import all components from simple_server
from simple_server import app

# Import additional modules if needed for direct execution
import uvicorn

# Start the server when this file is run directly
if __name__ == "__main__":
    print("Starting AgenticAI Integration Platform...")
    uvicorn.run("simple_server:app", host="0.0.0.0", port=8000, reload=True)
