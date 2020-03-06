# import the necessary packages
from collections import deque

import numpy as np
import argparse
import cv2
import imutils
import time
 
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-b", "--buffer", type=int, default=54,
	help="max buffer size")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)

# initialize the list of tracked points, the frame counter,
# and the coordinate deltas
pts = deque(maxlen=args["buffer"])
#print (pts, " ", len(pts))
#time.sleep(20)
counter = 0
(dX, dY) = (0,0)
direction = ""
 
# Grab a reference to the video file
left=cv2.VideoCapture(0)
right=cv2.VideoCapture(1)
# Set fps
left.set(5, 30) 
right.set(5, 30)

# allow the camera or video file to warm up
time.sleep(2.0)

def trackedObjectXYcoord (frame, contours, x, y)

# keep looping
while (True):
	# grab the current frame
	_, leftFrame = left.read()
	_, rightFrame = right.read()

	#_, leftFrame = left.retrieve()
	#_, rightFrame = right.retrieve()

	# blur frame, and convert it to the HSV
	leftFrame = imutils.resize(leftFrame, width=950)
	rightFrame = imutils.resize(rightFrame, width=950)
	leftblurred = cv2.GaussianBlur(leftFrame, (11, 11), 0)	
	rightblurred = cv2.GaussianBlur(rightFrame, (11, 11), 0)
	lefthsv = cv2.cvtColor(leftblurred, cv2.COLOR_BGR2HSV)
	righthsv = cv2.cvtColor(rightblurred, cv2.COLOR_BGR2HSV) 

	# construct a mask for the color "green", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	leftmask = cv2.inRange(lefthsv, greenLower, greenUpper)
	leftmask = cv2.erode(leftmask, None, iterations=2)
	leftmask = cv2.dilate(leftmask, None, iterations=2)

	rightmask = cv2.inRange(righthsv, greenLower, greenUpper)
	rightmask = cv2.erode(rightmask, None, iterations=2)
	rightmask = cv2.dilate(rightmask, None, iterations=2)

	# find contours in the mask and initialize the current
	# (x, y) center of the ball
	leftcnts = cv2.findContours(leftmask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	leftcnts = imutils.grab_contours(leftcnts)
	leftcenter = None

	rightcnts = cv2.findContours(rightmask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	rightcnts = imutils.grab_contours(rightcnts)
	rightcenter = None
 	
	# LEFT CAM
	# only proceed if at least one contour was found
	if (len(leftcnts) > 0) :
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
		leftc = max(leftcnts, key=cv2.contourArea)
		((lx, ly), radius) = cv2.minEnclosingCircle(leftc)
		M = cv2.moments(leftc)
		leftcenter = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
		if radius > 10:
		# draw the circle and centroid on the frame,
		# then update the list of tracked points
			cv2.circle(leftFrame, (int(lx), int(ly)), int(radius),(0, 255, 0), 2)
			cv2.circle(leftFrame, leftcenter, 5, (0, 255, 0), -1)

		# update the points queue
		pts.appendleft(leftcenter)
		# loop over the set of tracked points
	for i in range(1, len(pts)):
		# if either of the tracked points are None, ignore
		# them
		if pts[i - 1] is None or pts[i] is None:
			continue
 
		# check to see if enough points have been accumulated in
		# the buffer
		if counter >= 10 and i == 1 and pts[-10] is not None:
			# compute the difference between the x and y
			# coordinates and re-initialize the direction
			# text variables
			dX = pts[-10][0] - pts[i][0]
			dY = pts[-10][1] - pts[i][1]
			(dirX, dirY) = ("", "")
 
			# ensure there is significant movement in the
			# x-direction
			if np.abs(dX) > 20:
				dirX = "East" if np.sign(dX) == 1 else "West"
 

			# ensure there is significant movement in the
			# y-direction
			if np.abs(dY) > 20:
				dirY = "North" if np.sign(dY) == 1 else "South"
 
			# handle when both directions are non-empty
			if dirX != "" and dirY != "":
				direction = "{}-{}".format(dirY, dirX)
 
			# otherwise, only one direction is non-empty
			else:
				direction = dirX if dirX != "" else dirY

		# otherwise, compute the thickness of the line and
		# draw the connecting lines
		thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
		cv2.line(leftFrame, pts[i - 1], pts[i], (0, 0, 255), thickness)
	
	# RIGHT CAM
	# only proceed if at least one contour was found
	if (len(rightcnts) > 0) :
		rightc = max(rightcnts, key=cv2.contourArea)
		((rx, ry), radius) = cv2.minEnclosingCircle(rightc)
		M = cv2.moments(rightc)
		rightcenter = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
		# only proceed if the radius meets a minimum size
		if radius > 10:
			cv2.circle(rightFrame, (int(rx), int(ry)), int(radius),(0, 255, 255), 2)
			cv2.circle(rightFrame, rightcenter, 5, (0, 255, 255), -1)

		# update the points queue
		pts.appendleft(rightcenter)
		# loop over the set of tracked points
	for i in range(1, len(pts)):
		# if either of the tracked points are None, ignore them
		if pts[i - 1] is None or pts[i] is None:
			continue
 
		# check to see if enough points have been accumulated in
		# the buffer
		if counter >= 10 and i == 1 and pts[-10] is not None:
			# compute the difference between the x and y
			# coordinates and re-initialize the direction
			# text variables
			dX = pts[-10][0] - pts[i][0]
			dY = pts[-10][1] - pts[i][1]
			(dirX, dirY) = ("", "")
 
			# ensure there is significant movement in the
			# x-direction
			if np.abs(dX) > 20:
				dirX = "East" if np.sign(dX) == 1 else "West"
 

			# ensure there is significant movement in the
			# y-direction
			if np.abs(dY) > 20:
				dirY = "North" if np.sign(dY) == 1 else "South"
 
			# handle when both directions are non-empty
			if dirX != "" and dirY != "":
				direction = "{}-{}".format(dirY, dirX)
 
			# otherwise, only one direction is non-empty
			else:
				direction = dirX if dirX != "" else dirY

		# otherwise, compute the thickness of the line and
		# draw the connecting lines
		thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
		cv2.line(rightFrame, pts[i - 1], pts[i], (0, 255, 0), thickness)
 
	# show the movement deltas and the direction of movement on
	# the frame
	cv2.putText(leftFrame, direction, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
		0.65, (0, 0, 255), 3)
	cv2.putText(leftFrame, "dx: {}, dy: {}".format(dX, dY),
		(10, leftFrame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
		0.65, (0, 0, 255), 1)
	cv2.putText(rightFrame, direction, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
		0.65, (0, 0, 255), 3)
	cv2.putText(rightFrame, "dx: {}, dy: {}".format(dX, dY),
		(10, rightFrame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
		0.65, (0, 0, 255), 1)
			
	# show the frame to our screen
	cv2.imshow("LeftFrame", leftFrame)
	cv2.imshow("RightFrame", rightFrame)
	key = cv2.waitKey(1) & 0xFF
	counter+=1

	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		break

# release the camera
left.release()
right.release()
# close all windows
cv2.destroyAllWindows()
