#!/usr/bin/env python3

import serial
import asyncio
import websockets
import http.server
import socketserver
import json
import threading
import time
import queue
import json
from settings import SERIAL_PATH, WS_PORT, HTTP_PORT, URL_PATH
from web_server import run_web_server

dataQueue = queue.Queue(maxsize=10)
command = None

def serial_thread():
    global is_running
    global command
    is_running = True
    with serial.Serial(SERIAL_PATH, 9600, timeout=1) as ser:
        while is_running:
            line = ser.readline()
            update_data(line.strip())
            if command is not None:
                ser.write(str.encode(command))
                command = None

def update_data(s):
    if dataQueue.full():
        dataQueue.get()

    try:
        ss = s.decode('utf-8').split('-')
        if len(ss) != 2: 
            return
    except:
        return

    data = {
        "temp": int(ss[0]),
        "mois": int(ss[1]),
        "time": int(time.time()), 
    }
    dataQueue.put_nowait(json.dumps(data))

async def ws_server(websocket, path):
    global command
    while True:
        try:
            data = dataQueue.get(timeout=0.1)
            await websocket.send(data)
        except:
            pass

        try:
            clientData = await asyncio.wait_for(websocket.recv(), timeout=0.1)
            command = clientData
            if not command.endswith('\n'):
                command += '\n'
        except:
            pass

threading.Thread(target=serial_thread).start()
threading.Thread(target=run_web_server).start()

start_ws_server = websockets.serve(ws_server, URL_PATH, WS_PORT)
asyncio.get_event_loop().run_until_complete(start_ws_server)
asyncio.get_event_loop().run_forever()
