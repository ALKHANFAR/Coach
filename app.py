from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class SlackHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # Parse JSON
        try:
            data = json.loads(post_data.decode('utf-8'))
            if 'challenge' in data:
                # Respond to Slack challenge
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(data['challenge'].encode('utf-8'))
                return
        except:
            pass
        
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Slack Bot is running!")

if __name__ == '__main__':
    server = HTTPServer(('', 8000), SlackHandler)
    print("Server running on port 8000...")
    server.serve_forever()
