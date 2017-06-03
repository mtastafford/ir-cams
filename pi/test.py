import numpy as np
import cv2

#Create a black image
img = np.zeros((512,512,3), np.uint8)
cv2.circle(img,(447,63), 63, (0,0,255), -1)
cv2.namedWindow('image', cv2.WINDOW_NORMAL)
cv2.imshow('image',img)
cv2.waitKey(0)
cv2.destroyAllWindows()
