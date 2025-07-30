#!/usr/bin/env python3
"""
Standalone WebSocket test for reverse connections.
This file demonstrates how to send WebSocket requests through Envoy reverse connections.
"""

import socket
import base64
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_websocket_through_reverse_connection(port: int) -> bool:
    """
    Test sending a WebSocket connection through reverse connection.
    
    Args:
        port: The port of the cloud Envoy egress listener (e.g., 8085)
        
    Returns:
        bool: True if WebSocket connection succeeds, False otherwise
    """
    try:
        # Create a manual WebSocket handshake that works with HTTP/1.1
        # This is more compatible with reverse connection proxies
        def manual_websocket_handshake():
            try:
                # Create socket connection
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                sock.connect(('localhost', port))
                
                # Generate proper 16-byte random WebSocket key
                random_key = os.urandom(16)
                websocket_key = base64.b64encode(random_key).decode('utf-8')
                
                # Create WebSocket handshake request with reverse connection headers
                handshake_request = (
                    f"GET /ws/echo HTTP/1.1\r\n"
                    f"Host: localhost:{port}\r\n"
                    f"Upgrade: websocket\r\n"
                    f"Connection: Upgrade\r\n"
                    f"Sec-WebSocket-Key: {websocket_key}\r\n"
                    f"Sec-WebSocket-Version: 13\r\n"
                    f"x-remote-node-id: on-prem-node\r\n"  # Required for reverse connection
                    f"x-dst-cluster-uuid: on-prem\r\n"    # Required for reverse connection
                    f"\r\n"
                )
                
                logger.info(f"Sending WebSocket handshake to localhost:{port}")
                logger.info(f"Request headers:\n{handshake_request}")
                sock.send(handshake_request.encode('utf-8'))
                
                # Read handshake response
                response = sock.recv(4096).decode('utf-8')
                logger.info(f"WebSocket handshake response: {response[:200]}...")
                
                if "101 Switching Protocols" in response:
                    logger.info("✓ WebSocket handshake successful!")
                    
                    # Send a simple test message (WebSocket frame format)
                    test_msg = "Hello WebSocket through reverse connection!"
                    # Simple WebSocket text frame (unmasked for simplicity)
                    frame = bytearray([0x81])  # FIN=1, opcode=1 (text)
                    payload = test_msg.encode('utf-8')
                    
                    if len(payload) < 126:
                        frame.append(len(payload))
                        frame.extend(payload)
                    else:
                        # Handle longer payloads if needed
                        frame.append(126)
                        frame.extend(len(payload).to_bytes(2, 'big'))
                        frame.extend(payload)
                    
                    sock.send(frame)
                    logger.info(f"Sent WebSocket message: {test_msg}")
                    
                    # Try to read response (simple approach)
                    try:
                        sock.settimeout(5)
                        response_frame = sock.recv(1024)
                        if response_frame:
                            logger.info("✓ Received WebSocket response frame")
                            logger.info(f"Response frame length: {len(response_frame)} bytes")
                            return True
                        else:
                            logger.warning("No response received")
                            return False
                    except socket.timeout:
                        logger.warning("Timeout waiting for WebSocket response")
                        return False
                    finally:
                        sock.close()
                else:
                    logger.error(f"WebSocket handshake failed. Response: {response}")
                    sock.close()
                    return False
                    
            except Exception as e:
                logger.error(f"Manual WebSocket handshake error: {e}")
                return False
                
        # Run the manual handshake
        logger.info("Testing WebSocket connection through reverse connection (manual handshake)")
        result = manual_websocket_handshake()
        
        if result:
            logger.info("✓ WebSocket connection through reverse connection successful")
            return True
        else:
            logger.error("✗ WebSocket connection failed")
            return False
            
    except Exception as e:
        logger.error(f"Error testing reverse WebSocket connection: {e}")
        return False

def main():
    """Main function to run the WebSocket test."""
    logger.info("Starting WebSocket reverse connection test")
    
    # Test WebSocket through cloud Envoy egress port (8085)
    # This should route through the reverse connection to the on-prem WebSocket service
    cloud_egress_port = 8085
    
    success = test_websocket_through_reverse_connection(cloud_egress_port)
    
    if success:
        logger.info("🎉 WebSocket reverse connection test PASSED!")
    else:
        logger.error("❌ WebSocket reverse connection test FAILED!")
    
    return success

if __name__ == "__main__":
    main() 