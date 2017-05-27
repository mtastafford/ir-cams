import json
from websocket_server import WebsocketServer

class websocketserver:

        cams = {}
        beacons = {}
        users = {}
        
        port = 8001

# Called for every client connecting (after handshake)
        def new_client(self, client, server):
	        print("New client connected and was given id %d" % client['id'])
	        server.send_message_to_all("Hey all, a new client has joined us")
                server.send_message(client, str(client['id']))

# Called for every client disconnecting
        def client_left(self, client, server):
	        print("Client(%d) disconnected" % client['id'])

# Called when a client sends a message
        def message_received(self, client, server, message):
	        if len(message) > 1000:
		        message = message[:1000]+'..'
	#print("Client(%d) said: %s" % (client['id'], message))
                obj = json.loads(message);
                print(obj);
                print(type(obj));

        def __init__(self, host='0.0.0.0'):
                self.server = WebsocketServer(self.port, host)
                self.server.set_fn_new_client(self.new_client)
                self.server.set_fn_client_left(self.client_left)
                self.server.set_fn_message_received(self.message_received)
                self.server.run_forever()
