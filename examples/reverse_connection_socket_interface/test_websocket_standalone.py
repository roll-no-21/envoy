#!/usr/bin/env python3
"""
Standalone WebSocket test to verify the WebSocket server works before testing through reverse connections.
"""

import asyncio
import websockets
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_websocket_echo():
    """Test WebSocket echo functionality."""
    uri = "ws://localhost:8080/echo"
    test_messages = ["Hello WebSocket!", "Testing echo", "Goodbye!"]
    
    logger.info(f"Connecting to WebSocket at {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info("WebSocket connection established")
            
            # Send test messages and receive echoes
            for message in test_messages:
                logger.info(f"Sending: {message}")
                await websocket.send(message)
                
                # Wait for echo response
                response = await websocket.recv()
                logger.info(f"Received: {response}")
                
                if f"Echo: {message}" in response:
                    logger.info("✓ Echo response correct")
                else:
                    logger.error("✗ Echo response incorrect")
                    return False
            
            logger.info("✓ All WebSocket messages sent and echoed successfully")
            return True
            
    except Exception as e:
        logger.error(f"WebSocket test failed: {e}")
        return False

async def main():
    """Main test function."""
    logger.info("Starting standalone WebSocket test")
    
    success = await test_websocket_echo()
    
    if success:
        logger.info("✓ WebSocket test completed successfully!")
    else:
        logger.error("✗ WebSocket test failed!")
    
    return success

if __name__ == "__main__":
    try:
        # Use asyncio.run() if available (Python 3.7+), otherwise use get_event_loop()
        if hasattr(asyncio, 'run'):
            result = asyncio.run(main())
        else:
            # For Python < 3.7
            loop = asyncio.get_event_loop()
            try:
                result = loop.run_until_complete(main())
            finally:
                loop.close()
        exit(0 if result else 1)
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        exit(1) 