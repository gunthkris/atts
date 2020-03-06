# import the necessary packages

## ValueError: Unrecognized backend string 'plt': valid strings are
## ['GTK3Agg', 'GTK3Cairo', 'MacOSX', 'nbAgg', 'Qt4Agg', 'Qt4Cairo',
## 'Qt5Agg', 'Qt5Cairo', 'TkAgg', 'TkCairo', 'WebAgg', 'WX', 'WXAgg',
## 'WXCairo', 'agg', 'cairo', 'pdf', 'pgf', 'ps', 'svg', 'template']

import numpy as np
import cv2
from collections import deque
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import gi
gi.require_version('Gtk','3.0')
import argparse
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
greenLower = (50, 86, 30)
greenUpper = (64, 255, 255)

# initialize the list of tracked points, the frame counter,
# and the coordinate deltas
lpts = deque(maxlen=args["buffer"]) 
rpts = deque(maxlen=args["buffer"])
counter = 0
(ldX, ldY) = (0, 0)
(rdX, rdY) = (0, 0)
(lx, ly) = (0, 0)
(rx, ry) = (0, 0)
ldirection = ""
rdirection = ""
 
# Grab a reference to the video file
left=cv2.VideoCapture(0)
right=cv2.VideoCapture(1)
# Set fps
left.set(5, 30)
right.set(5, 30)

# allow the camera or video file to warm up
time.sleep(2.0)

def trackedObjectXYcoord (frame, cnts, fdX, fdY, pts, direction):
    # Set default (x, y) position if no target on screen
    (cx, cy) = (0, 0)
    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        (cx, cy) = center
 
        # only proceed if the radius meets a minimum size
        if radius > 10:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
 
        # update the points queue
        pts.appendleft(center)

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
            fdX = pts[-10][0] - pts[i][0]
            fdY = pts[-10][1] - pts[i][1]
            (dirX, dirY) = ("", "")
 
            # ensure there is significant movement in the x-direction
            if np.abs(fdX) > 20:
                dirX = "East" if np.sign(fdX) == 1 else "West"

            # ensure there is significant movement in the y-direction
            if np.abs(fdY) > 20:
                dirY = "North" if np.sign(fdY) == 1 else "South"
 
            # handle when both directions are non-empty
            if dirX != "" and dirY != "":
                direction = "{}-{}".format(dirY, dirX)

            # otherwise, only one direction is non-empty
            else:
                direction = dirX if dirX != "" else dirY

        # otherwise, compute the thickness of the line and
        # draw the connecting lines
        thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
        # print(pts[i - 1], " ", pts[i])
    return (fdX, fdY, pts, direction, cx, cy)

# MAIN PROGRAM LOOP
while (True):
    # grab the current frame
    _, leftFrame = left.read()
    _, rightFrame = right.read()

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

    # find contours in the mask and initialize the current (x, y) center of the ball
    leftcnts = cv2.findContours(leftmask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    leftcnts = imutils.grab_contours(leftcnts)
    leftcenter = None

    rightcnts = cv2.findContours(rightmask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    rightcnts = imutils.grab_contours(rightcnts)
    rightcenter = None
    
    # Call function for left frame
    (ldX, ldY, lpts, ldirection, lx, ly) = trackedObjectXYcoord (leftFrame, leftcnts, ldX, ldY, lpts, ldirection)
    # show the movement deltas and the direction of movement on the frame
    cv2.putText(leftFrame, ldirection, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
    0.65, (0, 0, 255), 3)
    cv2.putText(leftFrame, "x: {}, y: {}".format(lx, ly),
    (10, leftFrame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
    0.65, (0, 0, 255), 1)
    
    # Call function for right frame
    (rdX, rdY, rpts, rdirection, rx, ry) = trackedObjectXYcoord (rightFrame, rightcnts, rdX, rdY, rpts, rdirection)
    # show the movement deltas and the direction of movement on the frame
    cv2.putText(rightFrame, rdirection, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
    0.65, (0, 0, 255), 3)
    cv2.putText(rightFrame, "x: {}, y: {}".format(rx, ry),
    (10, rightFrame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
    0.65, (0, 0, 255), 1)
    
    # show the frame to our screen
    #cv2.imshow("LeftFrame", leftFrame)
    #cv2.imshow("RightFrame", rightFrame)
    print('yo')
    # disparity settings
    window_size = 5
    min_disp = 32
    num_disp = 112 - min_disp
    stereo = cv2.StereoSGBM_create(
        minDisparity = min_disp,
        numDisparities = num_disp,
        blockSize = window_size,
        uniquenessRatio = 10,
        speckleWindowSize = 100,
        speckleRange = 32,
        disp12MaxDiff = 1,
        P1 = 8*3*window_size**2,
        P2 = 32*3*window_size**2,
        mode = False
    )
    print('yo')
    #depth
    #stereo = cv2.StereoBM_create(numDisparities=16, blockSize=5)
    leftF = cv2.cvtColor(leftFrame, cv2.COLOR_BGR2GRAY)
    rightF = cv2.cvtColor(rightFrame, cv2.COLOR_BGR2GRAY)
    #cv2.imshow("LeftFrame", leftF)
    #cv2.imshow("RightFrame", rightF)

    #compute disparity
    disparity = stereo.compute(leftF,rightF).astype(np.float32) / 16.0
    print('yo')
    disparity = (disparity-min_disp)/num_disp
    print('yo')
    # morphology settings
    kernel = np.ones((12,12),np.uint8)
    # apply threshold
    threshold = cv2.threshold(disparity, 0.6, 1.0, cv2.THRESH_BINARY)[1]
    # apply morphological transformation
    morphology = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)
    print('yo')
    #cv2.imshow("gray", disparity)
    #plt.imshow(disparity)
    #plt.show()
    cv2.imshow('disparity', disparity)
    cv2.imshow('threshold', threshold)
    cv2.imshow('morphology', morphology)
    #print(disparity)
    # if the 'q' key is pressed, stop the loop
    key = cv2.waitKey(1) & 0xFF
    counter+=1
    if key == ord("q"):
        break

# release the camera
left.release()
right.release()
# close all windows
cv2.destroyAllWindows()
