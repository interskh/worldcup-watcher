import os
import SimpleHTTPServer
import SocketServer

index = 0


class MyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    _index = 0

    def __init__(self, *args, **kwargs):
        SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(
            self, *args, **kwargs)

    def do_GET(self):
        file_name = ".".join([str(MyHandler._index), "json"])
        current_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), file_name)
        print current_path
        if os.path.exists(current_path):
            with open(current_path, "r") as f:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(f.read())
        else:
            self.send_error(404, '404')
        MyHandler._index += 1

if __name__ == '__main__':
    httpd = SocketServer.TCPServer(("", 8597), MyHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.socket.close()
