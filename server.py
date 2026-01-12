#!/usr/bin/env python3
import http.server
import socketserver
import urllib.request
import urllib.parse
import json
import os

OLLAMA_URL = "http://localhost:11434"

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Proxy API requests to Ollama
        if self.path.startswith('/api/'):
            try:
                url = f"{OLLAMA_URL}{self.path}"
                with urllib.request.urlopen(url) as response:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(response.read())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(f"Error: {str(e)}".encode())
        else:
            # Serve static files
            super().do_GET()
    
    def do_POST(self):
        # Proxy API requests to Ollama
        if self.path.startswith('/api/'):
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                url = f"{OLLAMA_URL}{self.path}"
                req = urllib.request.Request(url, data=post_data, method='POST')
                req.add_header('Content-Type', 'application/json')
                
                with urllib.request.urlopen(req) as response:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(response.read())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(f"Error: {str(e)}".encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    PORT = 8080
    os.chdir('/app')
    
    with socketserver.TCPServer(("", PORT), ProxyHandler) as httpd:
        print(f"Web server with proxy running on port {PORT}")
        httpd.serve_forever()
