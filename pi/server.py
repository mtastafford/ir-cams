#import cv2
import json
import numpy as np
from websocket_server import WebsocketServer

class websocketserver:
 counter = 0
 cams = {}
 beacons = {}
 users = {}
 port = 8001
 #create 3D array of tracked areas (rows Area ID cols: xcen ycen width height)
 tAreas = np.zeros(shape=(10,6), dtype=int) #for now, track 10 areas. ID,xl, xr, yb, yt, pattern?
 #img = np.zeros((1024,1024,3), np.uint8)
 #cv2.circle(img,(tAreas[0, 1,], tAreas[0, 2]), 63, (0,0,255), -1)
 #cv2.namedWindow('image', cv2.WINDOW_NORMAL)
 #cv2.imshow('image',img)
 #cv2.destroyAllWindows()
 #Called for every client connecting (after handshake)
 def new_client(self, client, server):
  self.counter += 1;
  print("New client connected and was given id %d" % client['id'])
  server.send_message_to_all("Hey all, a new client has joined us")

 def client_left(self, client, server):
  print("Client(%d) disconnected" % client['id'])
 
 # Called when a client sends a message
 def message_received(self, client, server, message):
  if len(message) > 1000:
   message = message[:500]+'..'
  #print("Client(%d) said: %s" % (client['id'], message))
  obj = json.loads(message);
  #set client type in cams{} to match client ID
  self.cams[client['id']]=obj['type']
  ##check who sent message based on 'type' in JSON data (camera, beacon, etc.) then parse for client type
  if 'camera' in obj.values(): #if message from camera, it is found blobs.
   ##//TO DO -- MAKE 4D ARRAY TO ACCOUNT FOR MULTIPLE CAMERAS//##
   #####################################################################################
   #make n-dim array to store found blobs based on how many unique blobs were sent for n			
   for j in range(0,len(obj['blobs'])):
    found = np.ndarray(shape=(len(obj['blobs']),5,1), dtype=int)
    found[j,0,0]=obj['blobs'][j]['xloc']
    found[j,1,0]=obj['blobs'][j]['yloc']
    found[j,2,0]=obj['blobs'][j]['width']
    found[j,3,0]=obj['blobs'][j]['height']
    found[j,4,0]=0 ###0 if unmatched, 1 if matched
   #####################################################################################
   #####################################################################################
   #ANALYZE BLOBS FOUND
   #There are 3 cases. 
   #1)More found blobs than tracked areas. Including of tracked areas = 0
   #2)More tracked areas than found blobs.
   #3)Equal amount of blobs found & areas tracked
   #########################################
   #if amount found > areas tracked, compare each area to blob
   #list and see if any blobs fall in areas. 
   #i) remove blob from found list if matched??
   #ii) update matched area signal string with "1" for HIGH or "0" for LOW
   #iii) add unmatched found blobs as new areas w/ Signal string "1" to start
   ##################
   ### CASE 1 & 3 ###
   ##################
   #if len(obj['blobs'])>=(np.count_nonzero(self.tAreas[:,0])):
   print('Currently tracking %d areas' % np.count_nonzero(self.tAreas[:,0]), ' and found %d new blobs' % len(obj['blobs']))
   #test if found blob is within a tracked area				
   if not np.any(self.tAreas[0,:]): #check if tAreas list is empty
    #if empty, add all blobs to tracked areas
    print(len(obj['blobs']))
    for i in range(0,len(obj['blobs'])): #all all found blobs j to tAreas i
     self.tAreas[i,0]=i+1 #areaID
     self.tAreas[i,1]=found[i,0,0]-found[i,2,0]*2-10 #tAxL=fBX-1/2w
     self.tAreas[i,2]=found[i,0,0]+found[i,2,0]*2+10 #tAxR=fBX+1/2w
     self.tAreas[i,3]=found[i,1,0]-found[i,3,0]*2-10 #tAyB=fBy-1/2h
     self.tAreas[i,4]=found[i,1,0]+found[i,3,0]*2+10 #tAyT=fBy+1/2h
     #add signal string in here later
     print(self.tAreas)	
   ##################################################
   for i in range(0,np.count_nonzero(self.tAreas[:,0])): #testing each area i (replace 9 with np.count_nonzero(self.tAreas[:,0]) later)
    print('Checking tracked region: ' , self.tAreas[i,:]) #print x range being tested
    ####check if area i has a match in blob j
    self.tAreas[i,5]+=1
    for j in range(0,len(obj['blobs'])): #test against found blobs j
     print("Against found blob: ", found[j,:,0]) #print found x location being tested
     if (self.tAreas[i,1]<found[j,0,0]<self.tAreas[i,2] and self.tAreas[i,3]<found[j,1,0]<self.tAreas[i,4] and found[j,4,0] == 0): #if area matches unmatched found blob
      print (self.tAreas[i,1],found[j,0,0],self.tAreas[i,2]) #print successful match range
      print("Blob %d" % j, " is inside tracked area %d" % i) #declare match found
      self.tAreas[i,1]=found[i,0,0]-found[i,2,0]*2-10 #update range tAxL=fBX-1/2w
      self.tAreas[i,2]=found[i,0,0]+found[i,2,0]*2+10 #update tAxR=fBX+1/2w
      self.tAreas[i,3]=found[i,1,0]-found[i,3,0]*2-10 #update tAyB=fBy-1/2h
      self.tAreas[i,4]=found[i,1,0]+found[i,3,0]*2+10 #update tAyT=fBy+1/2h
      self.tAreas[i,5]=0 #reset counter to deletion
      found[j,4,0]=1 #mark found blob as matched
    if self.tAreas[i,5]>0:
     print("There are no matches for area %d" % i) #declare no match -- this can be deleted later. not useful. debugging only
     ####nothing matching tracked area. delete count +1
     self.tAreas[i,5]+=1
     if self.tAreas[i,5]>=500: ##if deleter count >= 10, delete area
      for k in range(0,6):
       self.tAreas[i,k]=0
   #############add unmatched blobs from found list to end of tracked areas, after deleting areas to be removed.
   for j in range(0,len(obj['blobs'])-1):
    if found[j,4,0]==0:
     self.tAreas[np.count_nonzero(self.tAreas[:,0]),0]=np.count_nonzero(self.tAreas[:,0]) #areaID
     self.tAreas[np.count_nonzero(self.tAreas[:,0]),1]=found[j,0,0]-found[j,2,0]*2-10 #tAxL=fBX-1/2w
     self.tAreas[np.count_nonzero(self.tAreas[:,0]),2]=found[j,0,0]+found[j,2,0]*2+10 #tAxR=fBX+1/2w
     self.tAreas[np.count_nonzero(self.tAreas[:,0]),3]=found[j,1,0]-found[j,3,0]*2-10 #tAyB=fBy-1/2h
     self.tAreas[np.count_nonzero(self.tAreas[:,0]),4]=found[j,1,0]+found[j,3,0]*2+10 #tAyT=fBy+1/2h
     found[j,4,0]=1
     print("Added blob %d" % j , " to tracked list")  
   
   print("Tracked Areas: ")
   print(self.tAreas)

 def __init__(self, host='0.0.0.0'):
  self.server = WebsocketServer(self.port, host)
  self.server.set_fn_new_client(self.new_client)
  self.server.set_fn_client_left(self.client_left)
  self.server.set_fn_message_received(self.message_received)
  self.server.run_forever()
                
                
