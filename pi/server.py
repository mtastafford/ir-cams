import json
import matplotlib.pyplot as plt
import numpy as np
from websocket_server import WebsocketServer

class websocketserver:
        counter = 0
        cams = {}
        beacons = {}
        users = {}
        
        port = 8001
	#create 3D array of tracked areas (rows Area ID cols: xcen ycen width height)
	tAreas = np.ndarray(shape=(10,4), dtype=int)

# Called for every client connecting (after handshake)
        def new_client(self, client, server):
                self.counter += 1;
	        print("New client connected and was given id %d" % client['id'])
	        server.send_message_to_all("Hey all, a new client has joined us")

        def client_left(self, client, server):
	        print("Client(%d) disconnected" % client['id'])
                
# Called when a client sends a message
        def message_received(self, client, server, message):
	        if len(message) > 1000:
		        message = message[:1000]+'..'
	#print("Client(%d) said: %s" % (client['id'], message))
                obj = json.loads(message);
		#set client type in cams{} to match client ID
		self.cams[client['id']]=obj['type']
		##check who sent message based on 'type' in JSON data (camera, beacon, etc.) then pa$
                if 'camera' in obj.values():
		##//TO DO -- MAKE 4D ARRAY TO ACCOUNT FOR MULTIPLE CAMERAS//##
			#make n-dim array to store found blobs based on how many unique blobs were sent for n
			found = np.ndarray(shape=(len(obj['blobs']),2,10), dtype=int)
			###for loop before can likely be removed. doesn't make much sense to track the 'found' blobs. should track areas and compare found to that.
			for j in  range(0,len(obj['blobs'])):
				found[j,0,0]=obj['blobs'][j]['yloc']
				found[j,1,0]=obj['blobs'][j]['xloc']
				for i in range(1,10):
					found[j,0,10-i]=found[j,0,9-i]
					found[j,1,10-i]=found[j,1,9-i]
			#check if found blobs are in tracked areas
			#for k in range(1,10):
			#	if
			print(found)
			print(found*2)
                
        def __init__(self, host='0.0.0.0'):
                self.server = WebsocketServer(self.port, host)
                self.server.set_fn_new_client(self.new_client)
                self.server.set_fn_client_left(self.client_left)
                self.server.set_fn_message_received(self.message_received)
                self.server.run_forever()
