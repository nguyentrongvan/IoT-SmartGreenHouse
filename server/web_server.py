from bottle import route, run, template
from settings import HTTP_PORT, URL_PATH, WS_PORT

html_content = '404 Not Found'

@route('/')
def index():
    global html_content
    return html_content

def run_web_server():    
    global html_content
    with open('./index.html', 'r') as index_file:
        html_content = template(index_file.read(), WEBSOCKET_PATH="ws://{}:{}".format(URL_PATH, WS_PORT))

    run(host=URL_PATH, port=HTTP_PORT)
