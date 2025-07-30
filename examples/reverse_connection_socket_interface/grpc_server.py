#!/usr/bin/env python3

import grpc
from concurrent import futures
import time
import logging

# Import the generated classes
import greeter_pb2
import greeter_pb2_grpc

# Enable reflection
from grpc_reflection.v1alpha import reflection

class GreeterServicer(greeter_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        logging.info(f"Received SayHello request: name={request.name}")
        return greeter_pb2.HelloResponse(
            message=f"Hello {request.name}! (from gRPC backend service)"
        )
    
    def SayHelloAgain(self, request, context):
        logging.info(f"Received SayHelloAgain request: name={request.name}")
        return greeter_pb2.HelloResponse(
            message=f"Hello again {request.name}! (from gRPC backend service)"
        )

def serve():
    logging.basicConfig(level=logging.INFO)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Add the servicer to the server
    greeter_pb2_grpc.add_GreeterServicer_to_server(GreeterServicer(), server)
    
    # Enable reflection
    SERVICE_NAMES = (
        greeter_pb2.DESCRIPTOR.services_by_name['Greeter'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    
    # Listen on port 50051
    listen_addr = '0.0.0.0:50051'
    server.add_insecure_port(listen_addr)
    
    logging.info(f"Starting gRPC server on {listen_addr}")
    server.start()
    
    try:
        while True:
            time.sleep(60*60*24)  # Sleep for a day
    except KeyboardInterrupt:
        logging.info("Shutting down gRPC server")
        server.stop(0)

if __name__ == '__main__':
    serve() 