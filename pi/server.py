import cv2
import json
import numpy as np
from websocket_server import WebsocketServer



class websocketserver:
 numcams=0
 nBlobs = 0
 cams = {}
 beacons = {}
 users = {}
 port = 8001
 calibCount = 0
 Points2D = np.float64([0.0,0.0])
 ticker = 0
 ptsCam1 = np.zeros(shape=(2,1), dtype=float)
 ptsCam2 = np.zeros(shape=(2,1), dtype=float)

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
  if len(message) > 1000 and 'camera' in message:
   message = message[:500]+'..'
  obj = json.loads(message)
  if 'calibrate' in obj:
   print "Store X as %s " % obj['calibrate']['X'], "and"
  #set client type in cams{} to match client ID
  ##check who sent message based on 'type' in JSON data (camera, beacon, etc.) then parse for client type
  if 'camera' in obj.values():
   self.numcams +=1
   self.cams[client['id']]={}
   self.cams[client['id']]['mac']=obj['id']
   self.cams[client['id']]['calibrated']=0
   self.cams[client['id']]['blobs']={}
   print self.cams
   ###CHECK IF CAMERA HAS BEEN CALIBRATED PREVIOUSLY###
   calbFile = open("calbList.json", "r")
   checker=json.loads(calbFile.read())
   #print checker
   if self.cams[client['id']]['mac'] in (checker['mac']):
    print "Found Calibrated Camera"
    self.cams[client['id']]['id']=client['id']
    self.cams[client['id']]['X'] = checker['mac'][obj['id']]['X']
    self.cams[client['id']]['Y'] = checker['mac'][obj['id']]['Y']
    self.cams[client['id']]['Z'] = checker['mac'][obj['id']]['Z']
    self.cams[client['id']]['pM0'] = checker['mac'][obj['id']]['pM0']
    self.cams[client['id']]['pM1']= checker['mac'][obj['id']]['pM1']
    self.cams[client['id']]['pM2']= checker['mac'][obj['id']]['pM2']
    self.cams[client['id']]['pM3']= checker['mac'][obj['id']]['pM3']
    self.cams[client['id']]['pM4']= checker['mac'][obj['id']]['pM4']
    self.cams[client['id']]['pM5']= checker['mac'][obj['id']]['pM5']
    self.cams[client['id']]['pM6']= checker['mac'][obj['id']]['pM6']
    self.cams[client['id']]['pM7']= checker['mac'][obj['id']]['pM7']
    self.cams[client['id']]['pM8']= checker['mac'][obj['id']]['pM8']
    self.cams[client['id']]['pM9']= checker['mac'][obj['id']]['pM9']
    self.cams[client['id']]['pM10']= checker['mac'][obj['id']]['pM10']
    self.cams[client['id']]['pM11']= checker['mac'][obj['id']]['pM11']    
    self.cams[client['id']]['calibrated']=1
   ###check for matching MAC address
  if 'point2D' in obj.values(): #if message from camera, it is found blobs.
   ####################CALIBRATE CAMERA IF NOT DONE YET######################################## 
   if self.cams[client['id']]['calibrated']==0:   ##check for calibration if point received
    #calibPts = np.float64([[0,0,1],[1,0,1],[1,1,1],[0,1,1],[-1,1,1],[-1,0,1],[-1,-1,1],[0,-1,1],[1,-1,1]])
    calibPts = np.float64([[0,0,0],[5.125,-3.875,0],[-5.125,-3.875,0],[-5.125,3.875,0],[5.125,3.875,0]])
    #user to physically move beacon to specific locations to calibrate room
    if self.calibCount <= 0:
     if self.ticker <= 0:
      print "Camera Calibration X-Y points"
      self.Points2D = np.zeros(shape=(5,len(self.cams)*2))
      print self.Points2D
      print 'Move beacon to %d' %calibPts[self.calibCount,0], 'm, %d' %calibPts[self.calibCount,1], 'm, %d' % calibPts[self.calibCount,2], 'm location and press enter to store 2d point'
      raw_input("....")
      self.ticker += 1
    self.ticker += 1
    print self.ticker
    if self.ticker >= 500: 
     self.calibCount += 1
     self.ticker = 0

    if self.calibCount >= 5:
     self.Points2D[self.calibCount-1,0] = obj['blobs'][0]['xloc']
     self.Points2D[self.calibCount-1,1] = obj['blobs'][0]['yloc']
     print self.Points2D
     print calibPts
     cameraMatrix = np.float64([[247.9139798, 0., 155.30251177], [0., 248.19822494, 100.74688813], [0., 0., 1.]])
     distCoeff = np.float64([-0.45977769, 0.29782977, -0.00162724, 0.00046035])
     ret, rvec, tvec = cv2.solvePnP(calibPts,self.Points2D,cameraMatrix,distCoeff)
     rotM_cam =	cv2.Rodrigues(rvec)[0]
     pose = -np.matrix(rotM_cam).T * np.matrix(tvec)
     camMatrix = np.append(cv2.Rodrigues(rvec)[0], tvec, 1)
     projectionMatrix = np.dot(cameraMatrix, camMatrix)
     self.cams[client['id']]['X'] = str(pose[0,0])
     self.cams[client['id']]['Y'] = str(pose[1,0])
     self.cams[client['id']]['Z'] = str(pose[2,0])
     self.cams[client['id']]['pM0']=str(projectionMatrix[0,0])
     self.cams[client['id']]['pM1']=str(projectionMatrix[1,0])
     self.cams[client['id']]['pM2']=str(projectionMatrix[2,0])
     self.cams[client['id']]['pM3']=str(projectionMatrix[0,1])
     self.cams[client['id']]['pM4']=str(projectionMatrix[1,1])
     self.cams[client['id']]['pM5']=str(projectionMatrix[2,1])
     self.cams[client['id']]['pM6']=str(projectionMatrix[0,2])
     self.cams[client['id']]['pM7']=str(projectionMatrix[1,2])
     self.cams[client['id']]['pM8']=str(projectionMatrix[2,2])
     self.cams[client['id']]['pM9']=str(projectionMatrix[0,3])
     self.cams[client['id']]['pM10']=str(projectionMatrix[1,3])
     self.cams[client['id']]['pM11']=str(projectionMatrix[2,3])

     self.cams[client['id']]['calibrated']=1 
     self.calibCount = 0
     with open('calbList.json', 'w') as outfile:
      json.dump(self.cams[client['id']], outfile)
     print "Calibrated!"

    if self.calibCount >= 1 and self.calibCount <= 4:
     if self.ticker <= 0 or self.ticker >= 500:
      self.Points2D[self.calibCount-1,0] = obj['blobs'][0]['xloc']
      self.Points2D[self.calibCount-1,1] = obj['blobs'][0]['yloc']
      print self.Points2D
      print 'Move beacon to %d' %calibPts[self.calibCount,0], 'm, %d' %calibPts[self.calibCount,1], 'm, %d' % calibPts[self.calibCount,2], 'm location and press enter to store 2d point'
      raw_input("....")
      self.ticker += 1
      print self.ticker 
      if self.ticker >= 500:
       self.calibCount += 1
       self.ticker = 0
     self.ticker += 1
     print self.ticker
  ####################################################################################
   self.cams[client['id']]['blobs'].clear()
   found = np.zeros(shape=(len(obj['blobs']),5), dtype=int)
  #####################################################################################
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
   #################################IF CAMERA IS CALIRATED, TRACK BLOBS###############
   if self.cams[client['id']]['calibrated'] == 1: ####ONLY RUNS IF CAMERA SENDING MESSAGE HAS BEEN CALIBRATED###
    for i in range(0,len(obj['blobs'])): #add all found blobs i to camera blobs
     self.cams[client['id']]['blobs'][i]={}
     self.cams[client['id']]['blobs'][i]['xloc']=obj['blobs'][i]['xloc']
     self.cams[client['id']]['blobs'][i]['yloc']=obj['blobs'][i]['yloc']
    print self.cams[client['id']]['blobs']
    if len(self.cams)>=2:
     print "The server thinks there are %i cameras" %len(self.cams)
     print "Trying to triangulate 3d points"
     pMat1=np.float64([[self.cams[1]['pM0'],self.cams[1]['pM1'],self.cams[1]['pM2'],self.cams[1]['pM3']],[self.cams[1]['pM4'],self.cams[1]['pM5'],self.cams[1]['pM6'],self.cams[1]['pM7']],[self.cams[1]['pM8'],self.cams[1]['pM9'],self.cams[1]['pM10'],self.cams[1]['pM11']]])
     pMat2=np.float64([[self.cams[2]['pM0'],self.cams[2]['pM1'],self.cams[2]['pM2'],self.cams[2]['pM3']],[self.cams[2]['pM4'],self.cams[2]['pM5'],self.cams[2]['pM6'],self.cams[2]['pM7']],[self.cams[2]['pM8'],self.cams[2]['pM9'],self.cams[2]['pM10'],self.cams[2]['pM11']]])  
     if self.cams[client['id']]['id'] is 1:
      #for a in range(0,len(self.cams[client['id']]['blobs'])):
      self.ptsCam1[0,0] = self.cams[client['id']]['blobs'][0]['xloc']
      self.ptsCam1[1,0] = self.cams[client['id']]['blobs'][0]['yloc']
      print self.ptsCam1
      print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!CLIENT ID 1 ABOVE"
     if self.cams[client['id']]['id'] is 2:
      #for a in range(0,len(self.cams[client['id']]['blobs'])):
      self.ptsCam2[0,0] = self.cams[client['id']]['blobs'][0]['xloc']
      self.ptsCam2[1,0] = self.cams[client['id']]['blobs'][0]['yloc']
      print self.ptsCam2
      print "CLIENT ID 2 ABOVE~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
     if np.any(self.ptsCam1) and np.any(self.ptsCam2):
      print "TRIANGULATING"
      points3d = cv2.triangulatePoints(pMat1, pMat2, self.ptsCam1, self.ptsCam2) 
      print points3d
    else:
     print "Two cameras required for triangulation"

 def __init__(self, host='0.0.0.0'):
  self.server = WebsocketServer(self.port, host)
  self.server.set_fn_new_client(self.new_client)
  self.server.set_fn_client_left(self.client_left)
  self.server.set_fn_message_received(self.message_received)
  self.server.run_forever()
                
                
