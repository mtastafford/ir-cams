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
 Points2D = np.empty((0,2), float)
 ticker = 0
 ptsCam1 = np.zeros(shape=(2,1), dtype=float)
 ptsCam2 = np.zeros(shape=(2,1), dtype=float)
 calbPts = np.empty((0,3), float)
 calb3D = {}

 #Called for every client connecting (after handshake)
 def new_client(self, client, server):
  print("New client connected and was given id %d" % client['id'])
  server.send_message_to_all("Hey all, a new client has joined us")
 #Called for every client disconnecting
 def client_left(self, client, server):
  print("Client(%d) disconnected" % client['id'])
 # Called when a client sends a message
 def message_received(self, client, server, message):
  #if message is super long, and not from camera, truncate with '..' after 500 char
  if len(message) > 1000 and 'camera' in message:
   message = message[:500]+'..'
  obj = json.loads(message)
  #if message contains XYZ of point for calibration, trigger all cameras to store the next blob it sees as XYZ
  if 'capture' in obj:
   print ("Storing X = %s " % obj['capture']['X'], " Y = %s " % obj['capture']['Y'], " Z = %s" % obj['capture']['Z'])
   currsize = len(self.calb3D)
   self.calb3D[currsize] = {}
   self.calb3D[currsize]['X'] = obj['capture']['X']
   self.calb3D[currsize]['Y'] = obj['capture']['Y']
   self.calb3D[currsize]['Z'] = obj['capture']['Z']
   print self.calb3D
   print "Telling all cameras to store next point"
   for addresses in self.cams:
    print "Enable calibrating mode for CAM %s" % self.cams[addresses]['mac']
    self.cams[addresses]['storenext']=1
    print self.cams[addresses]
  #set client type in cams{} to match client ID
  ##check who sent message based on 'type' in JSON data (camera, beacon, etc.) then parse for client type
  if 'camera' in obj.values():
   self.numcams +=1
   self.cams[client['id']]={}
   self.cams[client['id']]['mac']=obj['id']
   self.cams[client['id']]['calibrated']=0
   self.cams[client['id']]['storenext']=0
   self.cams[client['id']]['CalbPts']={}
   self.cams[client['id']]['blobs']={}
   print self.cams
   ###CHECK IF CAMERA HAS BEEN CALIBRATED PREVIOUSLY###
   calbFile = open("calbList.json", "r")
   checker=json.loads(calbFile.read())
   for cameras in checker:
    if self.cams[client['id']]['mac'] in (checker[cameras]['mac']):
     print "Found Calibrated Camera"
     self.cams[client['id']]['id']=client['id']
     self.cams[client['id']]['X'] = checker[cameras]['X']
     self.cams[client['id']]['Y'] = checker[cameras]['Y']
     self.cams[client['id']]['Z'] = checker[cameras]['Z']
     self.cams[client['id']]['pM0'] = checker[cameras]['pM0']
     self.cams[client['id']]['pM1'] = checker[cameras]['pM1']
     self.cams[client['id']]['pM2'] = checker[cameras]['pM2']
     self.cams[client['id']]['pM3'] = checker[cameras]['pM3']
     self.cams[client['id']]['pM4'] = checker[cameras]['pM4']
     self.cams[client['id']]['pM5'] = checker[cameras]['pM5']
     self.cams[client['id']]['pM6'] = checker[cameras]['pM6']
     self.cams[client['id']]['pM7'] = checker[cameras]['pM7']
     self.cams[client['id']]['pM8'] = checker[cameras]['pM8']
     self.cams[client['id']]['pM9'] = checker[cameras]['pM9']
     self.cams[client['id']]['pM10'] = checker[cameras]['pM10']
     self.cams[client['id']]['pM11'] = checker[cameras]['pM11']    
     self.cams[client['id']]['calibrated']=1
     self.cams[client['id']]['k0']=checker[cameras]['k0']
     self.cams[client['id']]['k1']=checker[cameras]['k1']
     self.cams[client['id']]['k2']=checker[cameras]['k2']
     self.cams[client['id']]['k3']=checker[cameras]['k3']
     self.cams[client['id']]['k4']=checker[cameras]['k4']
     self.cams[client['id']]['cM0']=checker[cameras]['cM0']
     self.cams[client['id']]['cM1']=checker[cameras]['cM1']
     self.cams[client['id']]['cM2']=checker[cameras]['cM2']
     self.cams[client['id']]['cM3']=checker[cameras]['cM3']
     self.cams[client['id']]['cM4']=checker[cameras]['cM4']
     self.cams[client['id']]['cM5']=checker[cameras]['cM5']
     self.cams[client['id']]['cM6']=checker[cameras]['cM6']
     self.cams[client['id']]['cM7']=checker[cameras]['cM7']
     self.cams[client['id']]['cM8']=checker[cameras]['cM8']

  if 'calibrate' in obj.values():
   for cameras in self.cams:
    self.calbPts = np.empty(shape=(0,3), dtype = float)
    self.Points2D = np.empty(shape=(0,2), dtype = float)
    for point in self.calb3D:
     p3d = np.array([[float(self.calb3D[point]['X']),float(self.calb3D[point]['Y']),float(self.calb3D[point]['Z'])]])
     p2d = np.array([[float(self.cams[cameras]['CalbPts'][point]['X']),float(self.cams[cameras]['CalbPts'][point]['Y'])]])
     self.calbPts = np.append(self.calbPts, p3d, 0)
     self.Points2D = np.append(self.Points2D, p2d, 0)
     print self.Points2D
     print self.calbPts
#    cameraMatrix = np.float64([[247.9139798, 0., 155.30251177], [0., 248.19822494, 100.74688813], [0., 0., 1.]])
#    distCoeff = np.float64([-0.45977769, 0.29782977, -0.00162724, 0.00046035])
    print "debug1"
    w = 319
    h = 199
    size = (w,h)
    self.calbPts = (self.calbPts).astype('float32')
    self.Points2D = (self.Points2D).astype('float32')
    ret, cameraMatrix, distCoeff, rvec, tvec = cv2.calibrateCamera([self.calbPts],[self.Points2D],size)
    rvec = np.array([[rvec[0][0,0]],[rvec[0][1,0]],[rvec[0][2,0]]])
    tvec = np.array([[tvec[0][0,0]],[tvec[0][1,0]],[tvec[0][2,0]]])
    rotM_cam =  cv2.Rodrigues(rvec)[0]
    pose = -np.matrix(rotM_cam).T * np.matrix(tvec)
    camMatrix = np.append(cv2.Rodrigues(rvec)[0], tvec, 1)
    projectionMatrix = np.dot(cameraMatrix, camMatrix)
    self.cams[cameras]['X'] = str(pose[0,0])
    self.cams[cameras]['Y'] = str(pose[1,0])
    self.cams[cameras]['Z'] = str(pose[2,0])
    self.cams[cameras]['pM0']=str(projectionMatrix[0,0])
    self.cams[cameras]['pM1']=str(projectionMatrix[1,0])
    self.cams[cameras]['pM2']=str(projectionMatrix[2,0])
    self.cams[cameras]['pM3']=str(projectionMatrix[0,1])
    self.cams[cameras]['pM4']=str(projectionMatrix[1,1])
    self.cams[cameras]['pM5']=str(projectionMatrix[2,1])
    self.cams[cameras]['pM6']=str(projectionMatrix[0,2])
    self.cams[cameras]['pM7']=str(projectionMatrix[1,2])
    self.cams[cameras]['pM8']=str(projectionMatrix[2,2])
    self.cams[cameras]['pM9']=str(projectionMatrix[0,3])
    self.cams[cameras]['pM10']=str(projectionMatrix[1,3])
    self.cams[cameras]['pM11']=str(projectionMatrix[2,3])
    self.cams[cameras]['calibrated']=1
    self.cams[cameras]['k0']=str(distCoeff[0,0])
    self.cams[cameras]['k1']=str(distCoeff[0,1]) 
    self.cams[cameras]['k2']=str(distCoeff[0,2]) 
    self.cams[cameras]['k3']=str(distCoeff[0,3]) 
    self.cams[cameras]['k4']=str(distCoeff[0,4]) 
    self.cams[cameras]['cM0']=str(cameraMatrix[0,0])
    self.cams[cameras]['cM1']=str(cameraMatrix[0,1])
    self.cams[cameras]['cM2']=str(cameraMatrix[0,2])
    self.cams[cameras]['cM3']=str(cameraMatrix[1,0])
    self.cams[cameras]['cM4']=str(cameraMatrix[1,1])
    self.cams[cameras]['cM5']=str(cameraMatrix[1,2])
    self.cams[cameras]['cM6']=str(cameraMatrix[2,0])
    self.cams[cameras]['cM7']=str(cameraMatrix[2,1])
    self.cams[cameras]['cM8']=str(cameraMatrix[2,2])
    
    print "Calibrated camera %s" % self.cams[cameras]['mac']
   with open('calbSave.json', 'w') as outfile:
    json.dump(self.cams, outfile)
    print "Wrote Camera info to File!!"


#######################DO NOT DELETE THE CALIBRATION STUFF BELOW############################
  
  if 'solve_cams' in obj.values():
   for cameras in self.cams:
    self.calbPts = np.empty((0,3), float)
    self.Points2D = np.empty((0,2), float)
    for point in self.calb3D:
     b = np.array([[float(self.calb3D[point]['X']),float(self.calb3D[point]['Y']),float(self.calb3D[point]['Z'])]])
     self.calbPts = np.concatenate((self.calbPts, b), axis = 0)
     c = np.array([[float(self.cams[cameras]['CalbPts'][point]['X']),float(self.cams[cameras]['CalbPts'][point]['Y'])]])
     self.Points2D = np.concatenate((self.Points2D, c), axis = 0)
    print self.Points2D
    print self.calbPts

    cameraMatrix = np.float64([[self.cams[cameras]['cM0'],self.cams[cameras]['cM1'],self.cams[cameras]['cM2']], [self.cams[cameras]['cM3'],self.cams[cameras]['cM4'],self.cams[cameras]['cM5']], [self.cams[cameras]['cM6'],self.cams[cameras]['cM7'],self.cams[cameras]['cM8']]])
    distCoeff = np.float64([self.cams[cameras]['k0'],self.cams[cameras]['k1'],self.cams[cameras]['k2'],self.cams[cameras]['k3'],self.cams[cameras]['k4']])
    print "debug1"
    ret, rvec, tvec = cv2.solvePnP(self.calbPts,self.Points2D,cameraMatrix,distCoeff)
    print "debug2"
    rotM_cam =	cv2.Rodrigues(rvec)[0]
    pose = -np.matrix(rotM_cam).T * np.matrix(tvec)
    camMatrix = np.append(cv2.Rodrigues(rvec)[0], tvec, 1)
    projectionMatrix = np.dot(cameraMatrix, camMatrix)
    print camMatrix
    print tvec
    print projectionMatrix
    print "does it break here?"
    self.cams[cameras]['X'] = str(pose[0,0])
    self.cams[cameras]['Y'] = str(pose[1,0])
    self.cams[cameras]['Z'] = str(pose[2,0])
    self.cams[cameras]['pM0']=str(projectionMatrix[0,0])
    self.cams[cameras]['pM1']=str(projectionMatrix[0,1])
    self.cams[cameras]['pM2']=str(projectionMatrix[0,2])
    self.cams[cameras]['pM3']=str(projectionMatrix[0,3])
    self.cams[cameras]['pM4']=str(projectionMatrix[1,0])
    self.cams[cameras]['pM5']=str(projectionMatrix[1,1])
    self.cams[cameras]['pM6']=str(projectionMatrix[1,2])
    self.cams[cameras]['pM7']=str(projectionMatrix[1,3])
    self.cams[cameras]['pM8']=str(projectionMatrix[2,0])
    self.cams[cameras]['pM9']=str(projectionMatrix[2,1])
    self.cams[cameras]['pM10']=str(projectionMatrix[2,2])
    self.cams[cameras]['pM11']=str(projectionMatrix[2,3])
    self.cams[cameras]['calibrated']=1

    print "Calibrated camera %s" % self.cams[cameras]['mac']
   with open('calbList.json', 'w') as outfile:
    json.dump(self.cams, outfile)
    print "Wrote Camera info to File!!"
##############################################################################################
  ####################################################################################

  if 'point2D' in obj.values(): #if message from camera, it is found blobs.
   ####################CALIBRATE CAMERA IF NOT DONE YET######################################## 
   self.cams[client['id']]['blobs'].clear()
   if self.cams[client['id']]['storenext']>=1: ##check for calibration if point received
    print "Storing point"
    currSize = len(self.cams[client['id']]['CalbPts'])
    self.cams[client['id']]['CalbPts'][currSize]={}
    self.cams[client['id']]['CalbPts'][currSize]['X']=obj['blobs'][0]['xloc']
    self.cams[client['id']]['CalbPts'][currSize]['Y']=obj['blobs'][0]['yloc']
    self.cams[client['id']]['storenext']=0  
   #################################IF CAMERA IS CALIRATED, TRACK BLOBS###############
   if self.cams[client['id']]['calibrated'] == 1: ####ONLY RUNS IF CAMERA SENDING MESSAGE HAS BEEN CALIBRATED###
    for i in range(0,len(obj['blobs'])): #add all found blobs i to camera blobs
     self.cams[client['id']]['blobs'][i]={}
     self.cams[client['id']]['blobs'][i]['xloc']=obj['blobs'][i]['xloc']
     self.cams[client['id']]['blobs'][i]['yloc']=obj['blobs'][i]['yloc']
    if len(self.cams[1]['blobs']) >= 1 and len(self.cams[2]['blobs']) >=1: ##if there are at least 2 cameras, try to triangulate
     pMat1=np.float64([[self.cams[1]['pM0'],self.cams[1]['pM1'],self.cams[1]['pM2'],self.cams[1]['pM3']],[self.cams[1]['pM4'],self.cams[1]['pM5'],self.cams[1]['pM6'],self.cams[1]['pM7']],[self.cams[1]['pM8'],self.cams[1]['pM9'],self.cams[1]['pM10'],self.cams[1]['pM11']]])
     pMat2=np.float64([[self.cams[2]['pM0'],self.cams[2]['pM1'],self.cams[2]['pM2'],self.cams[2]['pM3']],[self.cams[2]['pM4'],self.cams[2]['pM5'],self.cams[2]['pM6'],self.cams[2]['pM7']],[self.cams[2]['pM8'],self.cams[2]['pM9'],self.cams[2]['pM10'],self.cams[2]['pM11']]])  
     self.ptsCam1[0,0] = self.cams[1]['blobs'][0]['xloc']
     self.ptsCam1[1,0] = self.cams[1]['blobs'][0]['yloc']
#     print self.ptsCam1
     self.ptsCam2[0,0] = self.cams[2]['blobs'][0]['xloc']
     self.ptsCam2[1,0] = self.cams[2]['blobs'][0]['yloc']
#     print self.ptsCam2
     if np.any(self.ptsCam1) and np.any(self.ptsCam2):
#      print "TRIANGULATING"
      points3d = cv2.triangulatePoints(pMat1, pMat2, self.ptsCam1, self.ptsCam2) 
#      print points3d
#      print "------------was the output of triangulation----------------"
#      Grab the first three columns from the results to make a 3-N array and divide by 'w'
      p3d = np.array([(points3d[0]/points3d[3]),(points3d[1]/points3d[3]),(points3d[2]/points3d[3])])
      #Reshape to make a N-3 array
      p3d = p3d.reshape(-1,3)
      print p3d, "Triangulation results"
      #Make an array from the array resulting in [1,N,3]
      p3d = np.array([p3d])
      #Reshape camera matrix to a 4x4 for input into perspectiveTransform 
      #we'll just add zeros and a one to the last row.
      # from the TestTriangualtion function @, 
      #https://github.com/MasteringOpenCV/code/blob/master/Chapter4_StructureFromMotion/FindCameraMatrices.cpp
      A_24x4 = np.resize(pMat1,(4,4))
      A_24x4[3,0] = 0
      A_24x4[3,1] = 0
      A_24x4[3,2] = 0
      A_24x4[3,3] = 1 
      points3d_proj = cv2.perspectiveTransform(p3d, A_24x4)
      B_24x4 = np.resize(pMat2,(4,4))
      B_24x4[3,0] = 0
      B_24x4[3,1] = 0
      B_24x4[3,2] = 0
      B_24x4[3,3] = 1
      points3d_proj_2 = cv2.perspectiveTransform(p3d, B_24x4) 
#      print points3d_proj, "Transformed no.1"
#      print points3d_proj_2, "Transformed no.2"
    else:
     print "Two cameras required for triangulation"

 def __init__(self, host='0.0.0.0'):
  self.server = WebsocketServer(self.port, host)
  self.server.set_fn_new_client(self.new_client)
  self.server.set_fn_client_left(self.client_left)
  self.server.set_fn_message_received(self.message_received)
  self.server.run_forever()
                
                
