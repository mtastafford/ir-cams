import cv2
import json
import numpy as np
from websocket_server import WebsocketServer



class websocketserver:
 nBlobs = 0
 cams = {}
 beacons = {}
 users = {}
 port = 8001

 #create 3D array of tracked areas (rows Area ID cols: xcen ycen width height)
 tAreas = np.zeros((1,6), dtype=int) #for now, track 10 areas. ID,xl, xr, yb, yt, pattern?
 #Called for every client connecting (after handshake)
 def new_client(self, client, server):
  print("New client connected and was given id %d" % client['id'])
  server.send_message_to_all("Hey all, a new client has joined us")

 def client_left(self, client, server):
  print("Client(%d) disconnected" % client['id'])
 
 # Called when a client sends a message
 def message_received(self, client, server, message):
  if len(message) > 1000:
   message = message[:500]+'..'
  obj = json.loads(message);
  #set client type in cams{} to match client ID
  ##check who sent message based on 'type' in JSON data (camera, beacon, etc.) then parse for client type
  if 'camera' in obj.values(): #if message from camera, it is found blobs.
   self.cams.clear()
   self.cams[client['id']]={}
   found = np.zeros(shape=(len(obj['blobs']),5), dtype=int)
   #print(self.tAreas)
   ##//TO DO -- MAKE 4D ARRAY TO ACCOUNT FOR MULTIPLE CAMERAS//##
   #####################################################################################
   #make n-dim array to store found blobs based on how many unique blobs were sent for n			
   for j in range(0,len(obj['blobs'])):
    if j>len(obj['blobs']):
     break
    #print(obj['blobs'][j])
    found[j,0]=obj['blobs'][j]['xloc']
    found[j,1]=obj['blobs'][j]['yloc']
    found[j,2]=obj['blobs'][j]['width']
    found[j,3]=obj['blobs'][j]['height']
    found[j,4]=0 ###0 if unmatched, 1 if matched
   #print found
   #print self.tAreas
   #if len(obj['blobs'])>=(np.count_nonzero(self.tAreas[:,0])):
   #rint("CASE 1")
   #print len(obj['blobs'])
   #print found
   #print('Currently tracking %d areas' % np.count_nonzero(self.tAreas[:,0]), ' and found %d new blobs' % len(obj['blobs']))
   #test if found blob is within a tracked area				
   if not np.any(self.tAreas[0,:]): #check if tAreas list is empty
    #if empty, add all blobs to tracked areas
    #print("Adding all found blobs to empty list")
    for i in range(0,len(obj['blobs'])): #all all found blobs j to tAreas i
     self.nBlobs+=1
     self.tAreas=np.append(self.tAreas,[[self.nBlobs,found[i,0]-10,found[i,0]+10,found[i,1]-10,found[i,1]+10,0]],axis=0)
     #add signal string in here later
    self.tAreas=np.delete(self.tAreas,0,0) ##delete initial line of zeros from tracked areas.
   ##################################################
   for i in range(0,np.count_nonzero(self.tAreas[:,0])): #testing each area i (replace 9 with np.count_nonzero(self.tAreas[:,0]) later)
    #print('Checking tracked region: ' , self.tAreas[i,:]) #print x range being tested
    ####check if area i has a match in blob j
    self.tAreas[i,5]+=1
    for j in range(0,len(obj['blobs'])): #test against found blobs j
     #print("Against found blob: ", found[j,:]) #print found x location being tested
     if (self.tAreas[i,1]<found[j,0]<self.tAreas[i,2] and self.tAreas[i,3]<found[j,1]<self.tAreas[i,4] and found[j,4] == 0): #if area matches unmatched found blob
      #print (self.tAreas[i,1],found[j,0],self.tAreas[i,2]) #print successful match range
      #print("Blob %d" % j, " is inside tracked area %d" % i) #declare match found
      #print("Updating region defining tracked area %d" %i)
      self.tAreas[i,1]=found[j,0]-10
      self.tAreas[i,2]=found[j,0]+10
      self.tAreas[i,3]=found[j,1]-10
      self.tAreas[i,4]=found[j,1]+10
      self.tAreas[i,5]=0
      found[j,4]=1 #mark found blob as matched
      break
   for dlt in range(1,np.count_nonzero(self.tAreas[:,0])+1):
    if self.tAreas[np.count_nonzero(self.tAreas[:,0])-dlt,5]>=100: ##if deleter count >= 10, delete area
     #print("Row %d should be getting deleted" % i)
     self.tAreas = np.delete(self.tAreas,np.count_nonzero(self.tAreas[:,0])-i-1,0)
   #print(self.tAreas)
   #print(found)
   #print("Found %d blobs" % len(obj['blobs']))
   #############add unmatched blobs from found list to end of tracked areas, after deleting areas to be removed.
   for j in range(0,len(obj['blobs'])):
    if found[j,4]==0:
     #print("Adding apparently new blob %d" % j, " to tracked areas list")
     self.nBlobs+=1
     self.tAreas=np.append(self.tAreas,[[self.nBlobs,(found[j,0]-10),(found[j,0]+10),(found[j,1]-10),(found[j,1]+10),0]],axis=0)
     found[j,4]=1
   ############update dictionary for this camera in master blob list (holds all cameras data)
   for a in range(0,np.count_nonzero(self.tAreas[:,0])): #########cycle through all tracked areas 'a'
    #create new tracked blob in cam list for client id
    if self.tAreas[a,5]==0:
     self.cams[client['id']][a]={}
     self.cams[client['id']][a]['xloc']=str((self.tAreas[a,1]+self.tAreas[a,2])/2)
     self.cams[client['id']][a]['yloc']=str((self.tAreas[a,3]+self.tAreas[a,4])/2)
   print self.cams

 def __init__(self, host='0.0.0.0'):
  self.server = WebsocketServer(self.port, host)
  self.server.set_fn_new_client(self.new_client)
  self.server.set_fn_client_left(self.client_left)
  self.server.set_fn_message_received(self.message_received)
  self.server.run_forever()
                
                
