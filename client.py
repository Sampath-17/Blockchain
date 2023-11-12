# Importing the relevant libraries
import websockets
import asyncio

ls = []

# The main function that will handle connection and communication 
# with the server
async def listen():
    url = "ws://127.0.0.1:7890"
    # Connect to the server
    async with websockets.connect(url) as ws:
        messi = input("Enter your message: ")
        # Send a greeting message
        await ws.send(messi)
        # Stay alive forever, listening to incoming msgs
        while True:
            msg = await ws.recv()
            ls.append(msg)
            print(ls)

# Start the connection
asyncio.get_event_loop().run_until_complete(listen())
