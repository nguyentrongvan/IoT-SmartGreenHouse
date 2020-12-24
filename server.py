#!/usr/bin/env python3

import serial
import asyncio
import websockets
import json
import threading
import datetime
import queue

dataQueue = queue.Queue(maxsize=10)

def readingThread():
    global is_reading
    is_reading = True
    with serial.Serial('/dev/ttyUSB0', 9600, timeout=1) as ser:
        while is_reading:
            line = ser.readline()
            update_data(line.strip())

def update_data(s):
    if dataQueue.full():
        dataQueue.get()

    dataQueue.put_nowait("Recv: {} at {}".format(s, datetime.datetime.now()))

async def server(websocket, path):
    while True:
        try:
            data = dataQueue.get(timeout=0.1)
            await websocket.send(data)
        except:
            pass

        try:
            clientData = await asyncio.wait_for(websocket.recv(), timeout=0.1)
            print("Recv: {}".format(clientData))
        except:
            pass

start_server = websockets.serve(server, "localhost", 8999)

threading.Thread(target=readingThread).start()
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
