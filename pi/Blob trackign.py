# Standard imports
import cv2
import numpy as np;

xform=np.array([1,0,0,0,0,0])
xform.shape=(6,1)
font = cv2.FONT_HERSHEY_SIMPLEX
#line = cv2.LINE_AA
time = 0
attrib=6 ##(ID NUM, X, Y, SIZE, RESPONSE, MATCHED PREVIOUS?)##
bloblist=np.zeros((30,attrib))
#Capture 
cap = cv2.VideoCapture(0)
# Set up parameters for blob detection
params = cv2.SimpleBlobDetector_Params()
params.blobColor = 255
ID=0
params.filterByColor = True
params.minArea = 10
params.filterByArea = True
# Set up the detector with modified parameters.
detector = cv2.SimpleBlobDetector_create(params)
dthresh=3
delthresh=3
while(True):
	count=0
	# Capture frame-by-frame
	ret, frame = cap.read()	
	#Our operations on the frame come here
	keypoints = detector.detect(frame)
	#set blank array for detected blobs
	blobsfound = np.zeros((len(keypoints),attrib))
	#@print "----"
	
	##store found blobs ***ROW,X,Y,SIZE,RESPONSE***
	for kp in keypoints:
		blobsfound[count,0]=count
		blobsfound[count,1]=kp.pt[0]
		blobsfound[count,2]=kp.pt[1]
		blobsfound[count,3]=kp.size
		#mark all found blobs as unmatched and set loneliness to 0 of 5 max
		blobsfound[count,4]=0
		count = count + 1
		#print "(%d, %d) size=%.1f resp=%.1f" % (kp.pt[0], kp.pt[1], kp.size, kp.response)
		#cv2.circle(frame, (int(kp.pt[0]), int(kp.pt[1])), int(kp.size), (0, 0, 255))
		#cv2.putText(frame, str(count),(int(kp.pt[0]), int(kp.pt[1])), font, 1, (255,0,0),1, line)
	
	#UPDATE BLOBLIST WITH ALL BLOBS FOUND
	if len(keypoints)>1:
		#scan through BLOBLIST i
		for i in range(0,bloblist.shape[0]):
			#print "Frame = ", time
			#if bloblist is empty, send blobsfound to bloblist
			if int(bloblist[(1,0)]) == 0:
				bloblist = blobsfound
				print (blobsfound)
				print (bloblist)
				j = count
				break
			#else, check bloblist i vs blobsfound j & update if bloblist i ismatched...
			else:
				print (blobsfound)
				print (bloblist)
				for j in range(0,count):
					##########################################################
					## (IF FOUND_UNMATCHED & fX-<lX<fX+ & fY-<lY<fY+ ==> GO ##
					##########################################################
					if (blobsfound[(j,5)]==0) & ((blobsfound[(j,1)]-bloblist[(i,3)]*dthresh/2)<bloblist[(i,1)]<(blobsfound[(j,1)]+bloblist[(i,3)]*dthresh/2)) & ((blobsfound[(j,2)]-bloblist[(i,3)]*dthresh/2)<bloblist[(i,2)]<(blobsfound[(j,2)]+bloblist[(i,3)]*dthresh/2)):
						cv2.line(frame,(int(bloblist[(i,1)]),int(bloblist[(i,2)])),(int(blobsfound[(j,1)]),int(blobsfound[(j,2)])),(255,0,0),5)
						#set bloblist-i to blobfound-j
						bloblist[(i,2)]=blobsfound[(j,2)] ##**BLx = FBx
						bloblist[(i,1)]=blobsfound[(j,1)] ##**BLy = FBy
						bloblist[(i,4)]=1  ## Mark BlobList Entry as matched **COLUMN 5**
						bloblist[(1,5)]=0  ## Reset blob kill counter **COLUMN 6**
						blobsfound[(j,5)]=1 ## Mark blobfound Entry as matched **COLUMN 5**
						cv2.putText(frame, str(i),(int(bloblist[(i,1)]),int(bloblist[(i,2)])), font, 0.5, (255,0,0),1, line) ## Write ID Number (i = BL1) to image @ BL1 center
						#print 'MATCHED list ', i, 'with found ', j
						#print count
					##########################################
					## (IF STORED_MATCHES_NONE_FOUND --> GO ##
					##########################################				
				if (j == (count-1)) and (blobsfound[(j,5)]==0):# & ((blobsfound[(j,2)]-bloblist[(i,3)]*dthresh/2)<bloblist[(i,2)]<(blobsfound[(j,2)]+bloblist[(i,3)]*dthresh/2)):
					#print '--------------------------------------------------------'
					bloblist[(i,4)]=0
					bloblist[(i,5)] += 1 ##Increase blob kill counter by 1
					if bloblist[(i,5)]>=delthresh: ##If blob kill coutner hits 5
						bloblist=np.delete(bloblist,i,0) ##delete blob from bloblist
						#print 'deleted row ', i, '=============================================================================================================='
						cv2.putText(frame, 'x',(int(bloblist[(i,1)]),int(bloblist[(i,2)])), font, 0.5, (0,0,255),1, line)
					break

		#delete matcherows from found blobs
	if bloblist.all() != blobsfound.all():
		bloblist = np.vstack((bloblist, blobsfound[blobsfound[:,5]<1]))
			##add unmatched numbers to BLOBLIST
		
	#DELETE BLOB IF NOT MATCHED IN 5 FRAMES
	im_with_keypoints = cv2.drawKeypoints(frame, keypoints, np.array([]), (0,255,0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
	#gray = cv2.cvtColor(im_with_keypoints, cv2.COLOR_BGR2GRAY)
	# Display the resulting frame
	cv2.imshow('frame',im_with_keypoints)
	time = time + 1
	#@print blobsfound
	#@print 'Frame'
	if time==10:
		#print (bloblist)
		break
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
		
