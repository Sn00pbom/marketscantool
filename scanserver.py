from http.server import HTTPServer, BaseHTTPRequestHandler
import valuehunter as vh
from colorama import Fore
from io import StringIO
import pandas as pd


class ScanHandler(BaseHTTPRequestHandler):
    scan_func = None
    name_space = []

    def do_POST(self):
        """Serve POST Request"""
        datalen = int(self.headers['Content-Length'])
        wl_io = StringIO(self.rfile.read(datalen).decode('utf-8'))
        tos_wl_df = pd.read_csv(wl_io, header=5).iloc[0:-1]
        ScanHandler.name_space = [v for v in tos_wl_df['Symbol']]
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


def scan_macd(): # TODO use score wl macd thresh chain
    data_dict = {}
    for ticker in ScanHandler.name_space:
        data_dict[ticker] = vh.data.local.get_price_history(ticker)
    rubric = vh.grade.Rubric()
    rubric.add_column('MACD CL', lambda dd, t: vh.grade.macd.histogram_chain())


if __name__ == '__main__':
    # data_func = lambda: vh.data.local.get_price_history('ROKU')
    data_func = lambda: pd.DataFrame([[v] for v in ScanHandler.name_space], columns=['Symbol'])
    start_server(data_func)
