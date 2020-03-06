import cv2
import numpy as np
left =cv2.VideoCapture(0)
right=cv2.VideoCapture(1)
left.set(5, 30) # Set fps to 30
right.set(5, 30)


backLeftSub =  cv2.createBackgroundSubtractorMOG2()
backRightSub = cv2.createBackgroundSubtractorMOG2()

detectorParams = cv2.SimpleBlobDetector_Params()
detectorParams.minThreshold = 10
detectorParams.maxThreshold = 200
detectorParams.filterByArea = True
detectorParams.filterByColor = False
detectorParams.filterByCircularity = True
detectorParams.filterByConvexity = False
detectorParams.filterByInertia = False
detectorParams.minArea = 500
detectorParams.minCircularity = 0.7

detectorLeft  = cv2.SimpleBlobDetector_create(detectorParams)
detectorRight = cv2.SimpleBlobDetector_create(detectorParams)

# Capture loop from earlier...
while(True):
	if not(left.grab() and right.grab()):
		print("No more frames")
		break

	_, leftFrame = left.retrieve()
	_, rightFrame = right.retrieve()

	backLeft = backLeftSub.apply(leftFrame)
	backRight = backRightSub.apply(rightFrame)

	rawLeft = cv2.bitwise_and(leftFrame, leftFrame, mask = backLeft)
	rawRight = cv2.bitwise_and(rightFrame, rightFrame, mask = backRight)
	keysLeft = detectorLeft.detect(backLeft)
	keysRight = detectorRight.detect(backRight)

	detLeft = cv2.drawKeypoints(rawLeft, keysLeft, np.array([]), (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
	detRight = cv2.drawKeypoints(rawRight, keysRight, np.array([]), (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

	cv2.imshow('Left',  detLeft)
	cv2.imshow('Right',  detRight)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

left.release()
right.release()
cv2.destroyAllWindows()
