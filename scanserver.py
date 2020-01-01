from http.server import HTTPServer, BaseHTTPRequestHandler
import requests


def temp_func():
    return bytes('wewlad', 'utf-8')


class ScanHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        mimetype = 'text/plain'  # default case

        if self.path == '/':
            self.path = '/table.html'

        sendReply = False

        if self.path.endswith('.html'):
            mimetype = 'text/html'
            sendReply = True
        elif self.path.endswith('.css'):
            mimetype = 'text/css'
            sendReply = True
        elif self.path.endswith('.js'):
            mimetype = 'application/javascript'
            sendReply = True
        elif self.path.endswith('.jpg'):
            mimetype = 'image/jpg'
            sendReply = True

        if sendReply:
            try:
                with open('./webtable' + self.path, 'rb') as f:
                    self.send_response(200)
                    self.send_header('Content-type', mimetype)
                    self.end_headers()
                    self.wfile.write(f.read())

            except IOError as e:
                self.send_response(404)
                print(e)


if __name__ == '__main__':
    server = HTTPServer(('', 7531), ScanHandler)
    try:
        print('Server start')
        server.serve_forever()
    except KeyboardInterrupt:
        print('Server stop')
        server.socket.close()
