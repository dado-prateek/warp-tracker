#!/usr/bin/env python3

from http.server import HTTPServer,BaseHTTPRequestHandler

PORT = 1717

class myHandler(BaseHTTPRequestHandler):
	def do_HEAD(self):
		self.send_response(200)
		self.send_header('Content-type','text/html')
		self.end_headers()
		
	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-type','text/html')
		self.end_headers()
		if self.path == '/announce':
			self.wfile.write(bytes("announce", "utf-8"))
		else: 
			self.wfile.write(bytes("<h1>Welcome to the WARP BitTorrent tracker!</h1>",  "utf-8"))
		return
	
	
if __name__ == '__main__':	
	
	try:
		server = HTTPServer(('',PORT), myHandler)
		print ('Started WARP tracker on port', PORT)
	
		server.serve_forever()
	
	except KeyboardInterrupt:
		print ('Shutting down the server')
		server.socket.close()
