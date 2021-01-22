from bottle import get, run, template, static_file
from settings import HTTP_PORT, URL_PATH, WS_PORT

html_content = '404 Not Found'

@get('/')
def index():  
    with open('./client/index.html', 'r') as index_file:
        html_content = template(index_file.read(), WEBSOCKET_PORT=WS_PORT)
    return html_content

@get('/<filename:path>')
def js(filename):
    return static_file(filename, root='./client')

def run_web_server():    
    global html_content
    with open('./client/index.html', 'r') as index_file:
        html_content = template(index_file.read(), WEBSOCKET_PORT=WS_PORT)

    run(host=URL_PATH, port=HTTP_PORT, server='auto')
