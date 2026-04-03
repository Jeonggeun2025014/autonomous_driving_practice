"""
Simple WebSocket server for Raspberry Pi to receive commands from the web app and forward to motor control.

Protocol: receive text messages like `S:50;D:FORWARD`.

This example uses `websockets` and a placeholder `handle_motor(cmd)` function — replace with actual GPIO/PWM code.
"""
import asyncio
import websockets

async def handle_motor(cmd: str):
    # parse and handle the command
    print('Motor cmd:', cmd)
    # TODO: integrate with your motor driver (GPIO / pigpio / ROS topic)

async def handler(websocket, path):
    async for message in websocket:
        print('Received:', message)
        await handle_motor(message)
        await websocket.send('OK')

async def main():
    async with websockets.serve(handler, '0.0.0.0', 8765):
        print('WebSocket server started on ws://0.0.0.0:8765')
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())
