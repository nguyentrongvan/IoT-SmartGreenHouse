#!/usr/bin/env python3

import serial
import asyncio
import websockets
import socketserver
import threading
import time
import queue
import json
import random
from serial_read_line import ReadLine
from settings import SERIAL_PATH, WS_PORT, HTTP_PORT, URL_PATH, MAX_QUEUE_SIZE
from web_server import run_web_server

mutex = threading.Lock()
data_backlog = []
active_data_queue = queue.Queue(maxsize=MAX_QUEUE_SIZE)
command_queue = queue.Queue(maxsize=MAX_QUEUE_SIZE)
clients = set()

def serial_thread():
    global is_running

    is_running = True
    # while True:
    #     time.sleep(1)
    #     update_data('{}|{}'.format(random.randrange(25, 35), random.randrange(400, 600)).encode('utf-8'))

    with serial.Serial(SERIAL_PATH, 9600, timeout=1) as ser:
        reader = ReadLine(ser)        
        while is_running:
            line = reader.readline(timeout=0.2)
            if line is not None:
                update_data(line.strip())

            command = command_queue.get_nowait()
            if command is not None:
                ser.write(str.encode(command))

def update_data(s):        
    try:
        ss = s.decode('utf-8').split('|')
        if len(ss) != 2: 
            return
    except:
        return

    data = {
        "temp": int(ss[0]),
        "mois": int(ss[1]),
        "time": int(time.time() * 1000), 
    }

    if active_data_queue.full():
        add_to_backlog(active_data_queue.get_nowait())

    active_data_queue.put_nowait(data)

def add_to_backlog(data):
    mutex.acquire()
    if len(data_backlog) == MAX_QUEUE_SIZE:
        data_backlog.pop(0)
        
    data_backlog.append(data)
    mutex.release()

async def ws_server(websocket, path):

    mutex.acquire()
    try:
        await websocket.send(json.dumps(data_backlog))
    except:
        pass
    mutex.release()

    clients.add(websocket)
    try:    
        while True:        
            if not active_data_queue.empty():
                data = active_data_queue.get_nowait()
                str_data = json.dumps(data)

                await asyncio.wait([ ws.send(str_data) for ws in clients ])

                add_to_backlog(data)
                data = None

            try:
                client_data = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                command = client_data
                if not command.endswith('\n'):
                    command += '\n'

                command_queue.put_nowait(command)
            except (asyncio.TimeoutError, queue.Empty):
                continue
            except:
                break
    except:
        pass
    finally:
        clients.remove(websocket)

threading.Thread(target=serial_thread).start()
threading.Thread(target=run_web_server).start()

start_ws_server = websockets.serve(ws_server, URL_PATH, WS_PORT)
asyncio.get_event_loop().create_task
asyncio.get_event_loop().run_until_complete(start_ws_server)
asyncio.get_event_loop().run_forever()
