
import sys
from socket import *
import os
from datetime import datetime


serverPort = 8080
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('localhost', serverPort))
serverSocket.listen(1)
print(f'Server web attivo su http://localhost:{serverPort}')


MIME_TYPES = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.jpg': 'image/jpeg',
    '.png': 'image/png',
    '.ico': 'image/x-icon'
}

def get_content_type(filename):
    _, ext = os.path.splitext(filename)
    return MIME_TYPES.get(ext.lower(), 'application/octet-stream')

def log_request(addr, method, path, status):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {addr} - {method} {path} -> {status}")

while True:
    print('In attesa di connessioni...')
    connectionSocket, addr = serverSocket.accept()

    try:
        message = connectionSocket.recv(1024).decode()
        if not message:
            connectionSocket.close()
            continue

        parts = message.split()
        if len(parts) < 2:
            connectionSocket.close()
            continue

        method = parts[0]
        path = parts[1][1:]  

        if not path:
            path = 'index.html'

        filepath = os.path.join('www', path)

        if not os.path.isfile(filepath):
            response_body = "<h1>404 Not Found</h1>"
            response = (
                "HTTP/1.1 404 Not Found\r\n"
                "Content-Type: text/html\r\n"
                f"Content-Length: {len(response_body)}\r\n"
                "Connection: close\r\n"
                "\r\n"
                f"{response_body}"
            )
            connectionSocket.send(response.encode())
            log_request(addr, method, path, 404)
        else:
            with open(filepath, 'rb') as f:
                body = f.read()

            content_type = get_content_type(filepath)
            header = (
                "HTTP/1.1 200 OK\r\n"
                f"Content-Type: {content_type}\r\n"
                f"Content-Length: {len(body)}\r\n"
                "Connection: close\r\n"
                "\r\n"
            ).encode()
            connectionSocket.sendall(header + body)
            log_request(addr, method, path, 200)

    except Exception as e:
        print("Errore:", e)

    finally:
        connectionSocket.close()

