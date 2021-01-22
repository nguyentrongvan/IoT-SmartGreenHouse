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
from settings import SERIAL_PATH, WS_PORT, HTTP_PORT, URL_PATH, MAX_QUEUE_SIZE, AUTO_SETTINGS
from web_server import run_web_server

mutex = threading.Lock()
data_backlog = []
active_data_queue = queue.Queue(maxsize=MAX_QUEUE_SIZE)
command_queue = queue.Queue(maxsize=MAX_QUEUE_SIZE)
clients = set()
is_auto = True
unstable_count = 0

def serial_thread():
    global is_running
    global is_auto

    is_running = True
    # while True:
    #     time.sleep(1)
    #     update_data('{}|{}|true|true'.format(random.randrange(25, 35), random.randrange(400, 600)).encode('utf-8'))
    #     try:
    #         command_queue.get_nowait()
    #     except:
    #         pass

    with serial.Serial(SERIAL_PATH, 9600, timeout=1) as ser:
        reader = ReadLine(ser)        
        while is_running:
            line = reader.readline(timeout=0.2)
            if line is not None:
                update_data(line.strip())

            try:
                command = command_queue.get_nowait()

                if not command.endswith('\n'):
                    command += '\n'

                if command.endswith('auto\n'):
                    is_auto = command.startswith('s')                
                else:
                    ser.write(str.encode(command))
            except queue.Empty:
                pass

def update_data(s):        
    global is_auto
    global unstable_count

    try:
        ss = s.decode('utf-8').split('|')
        if len(ss) != 4: 
            return
    except:
        return

    data = {
        'temp': int(ss[0]),
        'mois': int(ss[1]),
        'light': ss[2].lower() == 'true',
        'fan': ss[3].lower() == 'true',
        'auto': is_auto,
        'time': int(time.time() * 1000),
    }

    if (AUTO_SETTINGS['mois'][0] < data['mois'] < AUTO_SETTINGS['mois'][1]) and (AUTO_SETTINGS['temp'][0] < data['temp'] < AUTO_SETTINGS['temp'][1]):
        unstable_count -= 1

    if is_auto:
        if  data['temp'] > AUTO_SETTINGS['temp'][1]:
            unstable_count += 1

            if not data['fan']:
                command_queue.put_nowait('start fan')
            if data['light']:
                command_queue.put_nowait('pause light')
        elif data['temp'] < AUTO_SETTINGS['temp'][0]:
            unstable_count += 1

            if data['fan']:
                command_queue.put_nowait('pause fan')
            if not data['light']:
                command_queue.put_nowait('start light')
        else:
            if data['fan']:
                command_queue.put_nowait('pause fan')
            if data['light']:
                command_queue.put_nowait('pause light')

    if not (AUTO_SETTINGS['mois'][0] < data['mois'] < AUTO_SETTINGS['mois'][1]):
        unstable_count += 1

    if unstable_count >= AUTO_SETTINGS['warn']:
        is_auto = False
        data['auto'] = False
        data['warn'] = True

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
