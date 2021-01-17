#!/usr/bin/env python3

import serial
import asyncio
import websockets
import json
import threading
import time
import queue
import json

dataQueue = queue.Queue(maxsize=10)
cmd = None

def serialThread():
    global is_running
    global cmd
    is_running = True
    with serial.Serial('/dev/ttyUSB0', 9600, timeout=1) as ser:
        while is_running:
            line = ser.readline()
            update_data(line.strip())
            if cmd is not None:
                if not cmd.endswith('\n'):
                    cmd += '\n'

                ser.write(str.encode(cmd))
                cmd = None

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

async def server(websocket, path):
    global cmd
    while True:
        try:
            data = dataQueue.get(timeout=0.1)
            await websocket.send(data)
        except:
            pass

        try:
            clientData = await asyncio.wait_for(websocket.recv(), timeout=0.1)
            cmd = clientData
        except:
            pass

start_server = websockets.serve(server, "localhost", 8999)

threading.Thread(target=serialThread).start()
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
