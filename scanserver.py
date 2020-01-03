from http.server import HTTPServer, BaseHTTPRequestHandler
import valuehunter as vh
from colorama import Fore


class ScanHandler(BaseHTTPRequestHandler):
    scan_func = None

    def do_GET(self):
        mimetype = 'text/plain'  # default case

        if self.path == '/':
            self.path = '/table.html'

        send_reply = False

        if self.path.endswith('.html'):
            mimetype = 'text/html'
            send_reply = True
        elif self.path.endswith('.css'):
            mimetype = 'text/css'
            send_reply = True
        elif self.path.endswith('.js'):
            mimetype = 'application/javascript'
            send_reply = True
        elif self.path.endswith('.json'):
            mimetype = 'application/json'
            send_reply = True
        elif self.path.endswith('.jpg'):
            mimetype = 'image/jpg'
            send_reply = True

        if send_reply:
            try:
                self.send_response(200)
                self.send_header('content-type', mimetype)
                self.end_headers()
                if self.path == '/data.json':
                    self.wfile.write(self.get_table_data())
                else:
                    with open('./webtable' + self.path, 'rb') as f:
                        self.wfile.write(f.read())

            except IOError as e:
                self.send_response(404)
                print(e)

    def get_table_data(self):
        df = ScanHandler.scan_func()
        jsf = df.to_json(orient='records')
        return bytes(jsf, 'utf-8')


def start_server(scan_function):
    ScanHandler.scan_func = scan_function
    server = HTTPServer(('', 7531), ScanHandler)
    try:
        print(Fore.GREEN + 'Server start')
        server.serve_forever()
    except KeyboardInterrupt:
        print(Fore.GREEN + 'Server stop')
        server.socket.close()


if __name__ == '__main__':
    data_func = lambda: vh.data.local.get_price_history('ROKU')
    start_server(data_func)
