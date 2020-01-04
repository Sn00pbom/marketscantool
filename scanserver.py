from http.server import HTTPServer, BaseHTTPRequestHandler
from colorama import Fore
from io import StringIO

import pandas as pd

from score_wl_macd_thresh_chain import score_macd_thresh_chain


class ScanHandler(BaseHTTPRequestHandler):
    scan_func = None
    namespace = []

    def do_POST(self):
        """Serve POST Request"""
        datalen = int(self.headers['Content-Length'])
        wl_io = StringIO(self.rfile.read(datalen).decode('utf-8'))
        tos_wl_df = pd.read_csv(wl_io, header=5).iloc[0:-1]
        ScanHandler.namespace = [v for v in tos_wl_df['Symbol']]
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        """Serve GET Request"""
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
                    self.wfile.write(ScanHandler.get_table_data())
                else:
                    with open('./webtable' + self.path, 'rb') as f:
                        self.wfile.write(f.read())

            except IOError as e:
                self.send_response(404)
                print(e)

    @staticmethod
    def get_table_data():
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


def score_table_func(namespace):
    df = score_macd_thresh_chain(namespace)
    df = df.reset_index()
    df = df.rename(columns={'index': 'Symbol'})
    return df


if __name__ == '__main__':
    data_func = lambda: score_table_func(ScanHandler.namespace)
    start_server(data_func)
