import asyncio
import websockets

async def server(websocket):
    message = await websocket.recv()
    print(f"Server received: {message}")
    await websocket.send(f"Echo: {message}")

async def client():
    async with websockets.connect("ws://localhost:8765") as websocket:
        await websocket.send("hello from patient")
        response = await websocket.recv()
        print(f"Client received: {response}")

async def main():
    async with websockets.serve(server, "localhost", 8765):
        await client()

asyncio.run(main())