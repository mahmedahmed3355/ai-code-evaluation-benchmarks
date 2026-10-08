from http.server import BaseHTTPRequestHandler, HTTPServer
import json, os
VERSION=os.environ.get("APP_VERSION","2.4.1")
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path=="/healthz":
            self.send_response(200); self.end_headers(); self.wfile.write(b"ok")
        elif self.path=="/version":
            self.send_response(200); self.end_headers(); self.wfile.write(VERSION.encode())
        elif self.path=="/data":
            self.send_response(200); self.send_header("Content-Type","application/json"); self.end_headers()
            self.wfile.write(json.dumps({"service":"ledger","version":VERSION}).encode())
        else:
            self.send_response(404); self.end_headers()
    def log_message(self,*a): pass
HTTPServer(("0.0.0.0",8080),H).serve_forever()
