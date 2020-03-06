import cv2
import numpy as np
left =cv2.VideoCapture(0)
right=cv2.VideoCapture(1)
left.set(5, 30) # Set fps to 30
right.set(5, 30)
counter = 0

while(True):
	if not(left.grab() and right.grab()):
		print("No more frames")
		break

	_, leftFrame = left.retrieve()
	_, rightFrame = right.retrieve()
	
	#print (counter)
	#counter+=1

	
	cv2.imshow('Left', leftFrame)
	cv2.imshow('Right', rightFrame)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

left.release()
right.release()
cv2.destroyAllWindows()
