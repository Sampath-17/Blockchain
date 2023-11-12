# Importing the relevant libraries
import websockets
import asyncio

# Server data
PORT = 7891
print("Server listening on Port " + str(PORT))

# A set of connected ws clients
connected = set()

# The main behavior function for this server
async def echo(websocket, path):
    # Store a copy of the connected client
    connected.add(websocket)
    # Handle incoming messages
    print("A client just connected" + str(websocket))
    try:
        async for message in websocket:
            print("Received message from client: " + message)
            # Send a response to all connected clients except sender
            for conn in connected:
                await conn.send("Someone said: " + message)
    # Handle disconnecting clients 
    except websockets.exceptions.ConnectionClosed as e:
        print("A client just disconnected")
    finally:
        connected.remove(websocket)

# Start the server
start_server = websockets.serve(echo, "localhost", PORT)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
