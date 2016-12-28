from pixy import *
from ctypes import *
import numpy as np
from numpy.linalg import inv

# Pixy Python SWIG get blocks example #
dt=0.02 #TIME STEP -- 0.02 = 50Hz AS PER PIXYCAM
A=np.array([(1,dt,0,0),(0,1,0,0),(0,0,1,dt),(0,0,0,1)]) #STATE MATRIX DEFINING HOW X & Y POS,VEL,ACCL UPDATE
AT=A.transpose() #TRANSPOSE OF STATE MATRIX

Xkp=np.array([(50),(3),(100),(5)]) #PAST STATE VECTOR DEFINIng t-1 Px, Py, Vx, Vy
Pk=np.zeros(16).reshape(4,4)#PREVIOUS STATE COVARIANCE MATRIX DEFINING INITIAL COVAR EST.
Pkp=np.array([(1,0.2,0.03,.005),(0.2,1,0.05,0.06),(0.03,0.05,1.0,0.9),(0.005,0.06,0.9,1.0)])#PROJECTED STATE  COVAR.
HIST=np.zeros(40).reshape(10,4) #USE THIS TO LOG THE LAST 10 TIMESTEPS, TO CALC COVAR.

#np.fill_diagonal(Pkp,1) #FILL DIAGONAL OF Pkp to assume initial covariances.
K=np.array([(0,0),(0,0),(0,0),(0,0)]) #Kalman Filter Placeholder
H=np.array([(1,0,0,0),(0,0,1,0)]) #Identity matrix skeleton to transform state vector to position vector
HT=H.transpose() #TRANSPOSE OF IDENTITY MATRIX
R=np.array([(0.01,0.02),(0.02,0.01)])
I=np.zeros(16).reshape(4,4) #4x4 identity
np.fill_diagonal(I,1) #Fill diagonal of I
print ("Kalman Filter of Blob Data from Get Blocks")
Xkf=A.dot(Xkp) #PREDICTED STATE BASED ON PREVIOUS STATE AND TIME ELAPSED
Xk=np.array([(0),(0),(0),(0)])

# Initialize Pixy Interpreter thread #
pixy_init()

class Blocks (Structure):
  _fields_ = [ ("type", c_uint),
               ("signature", c_uint),
               ("x", c_uint),
               ("y", c_uint),
               ("width", c_uint),
               ("height", c_uint),
               ("angle", c_uint) ]
kill=0
blocks = BlockArray(100)
frame  = 0
text_file = open("Output.txt", "w")
text_file.write("Measured:\tEstimated:\t\t\tUpdated:\n")
# Wait for blocks #
while 1:
  count = pixy_get_blocks(100, blocks)
  if count > 0:
  # Blocks found #
    print 'frame %3d:' % (frame)
    frame = frame + 1
    for index in range (0, count):
      #print '[BLOCK_TYPE=%d SIG=%d X=%3d Y=%3d WIDTH=%3d HEIGHT=%3d]' % (blocks[index].type, blocks[index].signature, blocks[index].x, blocks[index].y, blocks[index].width, blocks[index].height)
      Zk=np.array([(blocks[index].x),(blocks[index].y)])#Measurement
      Xkf=A.dot(Xkp) #Project the state ahead
      Pkf=(A.dot(Pkp)).dot(AT) #Project the Covariance ahead
      K=(Pkf.dot(HT)).dot(inv((H.dot(Pkf)).dot(HT)+R.transpose())) #Compute Kalman Gain
      text_file.write("%s\t" % Zk) #write frames measured value to file
      text_file.write("%s\t" % H.dot(Xkf)) #write frames estimated value to file
      #print("Kalman Gain")
      #print(inv((H.dot(Pkf)).dot(HT)+R.transpose()))
      #print(K)
      #print("Previous State")
      #print(Xkp)
      #print("Projected State - Px Vx Py Vr")
      #print(Xkf)
      Xk=Xkp+K.dot(Zk-H.dot(Xkf)) #Update state estimate via Kalman gain applied to measurement & estimate
      text_file.write("%s\n" % H.dot(Xk)) #write frames updated position to file
      Pk=(I-K.dot(H)).dot(Pkf) #Update covariance
      #print("Measured Position")
      #print(Zk)
      #print("Updated State")
      #print(Xk)
      #print("Estimated Covariance")
      #print(Pkp)
      #print("Updated Covariance")
      #print(Pk)
      Xkp=Xk
      Pkp=Pk
text_file.close()
      #for i in range(0,9):
      #	for j in range(0,4):
      #    HIST.itemset((9-i,j),HIST.item((9-i-1,j)))
      #for k in range(0,4):
      #      HIST.itemset((0,k),Xk.item(k))
      #print(HIST)
