from http.server import HTTPServer, BaseHTTPRequestHandler
import json


def get_table_data():
    d = [
        {"column1": "a", "column2": "b"},
        {"column1": "c", "column2": "d"},
        {"column1": "e", "column2": "f"},
    ]
    jsf = json.dumps(d)
    return bytes(jsf, 'utf-8')


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
        elif self.path.endswith('.json'):
            mimetype = 'application/json'
            sendReply = True
        elif self.path.endswith('.jpg'):
            mimetype = 'image/jpg'
            sendReply = True

        if sendReply:
            try:
                self.send_response(200)
                self.send_header('content-type', mimetype)
                self.end_headers()
                if self.path == '/data.json':
                    self.wfile.write(get_table_data())
                else:
                    with open('./webtable' + self.path, 'rb') as f:
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
