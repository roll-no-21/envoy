#!/usr/bin/env python3
"""
Simple WebSocket echo server for testing reverse connection WebSocket support.
"""

import asyncio
import logging
import websockets
from websockets.server import serve

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def echo_handler(websocket, path):
    """Handle WebSocket connections and echo back any messages received."""
    client_addr = websocket.remote_address
    logger.info(f"WebSocket client connected from {client_addr}, path: {path}")
    
    try:
        async for message in websocket:
            logger.info(f"Received message from {client_addr}: {message}")
            # Echo the message back to the client
            echo_message = f"Echo: {message}"
            await websocket.send(echo_message)
            logger.info(f"Sent echo to {client_addr}: {echo_message}")
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"WebSocket client {client_addr} disconnected")
    except Exception as e:
        logger.error(f"Error handling WebSocket connection from {client_addr}: {e}")

async def main():
    """Start the WebSocket server."""
    host = "0.0.0.0"
    port = 8080
    
    logger.info(f"Starting WebSocket echo server on {host}:{port}")
    
    # Start the WebSocket server
    async with serve(echo_handler, host, port):
        logger.info(f"WebSocket echo server running on ws://{host}:{port}")
        logger.info("Server will echo back any messages received")
        
        # Keep the server running
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        # Use asyncio.run() if available (Python 3.7+), otherwise use get_event_loop()
        if hasattr(asyncio, 'run'):
            asyncio.run(main())
        else:
            # For Python < 3.7
            loop = asyncio.get_event_loop()
            try:
                loop.run_until_complete(main())
            finally:
                loop.close()
    except KeyboardInterrupt:
        logger.info("WebSocket server stopped by user")
    except Exception as e:
        logger.error(f"WebSocket server error: {e}") 