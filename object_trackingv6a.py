# import the necessary packages
from collections import deque

import numpy as np
import argparse
import cv2 as cv
import time, sys
import imutils
 
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
left = cv.VideoCapture(0, cv.CAP_V4L2)
right = cv.VideoCapture(1, cv.CAP_V4L2)
# If we can't get images from both sources, error
if not left.isOpened() and not right.isOpened():  
        print("Can't opened the streams!")
        sys.exit(-9)

# Set fps
left.set(5, 30)
right.set(5, 30)
# Change the resolution
right.set(cv.CAP_PROP_FRAME_WIDTH, 640)  # float
right.set(cv.CAP_PROP_FRAME_HEIGHT, 480)  # float
left.set(cv.CAP_PROP_FRAME_WIDTH, 640)  # float
left.set(cv.CAP_PROP_FRAME_HEIGHT, 480)  # float

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
        c = max(cnts, key=cv.contourArea)
        ((x, y), radius) = cv.minEnclosingCircle(c)
        M = cv.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        (cx, cy) = center
 
        # only proceed if the radius meets a minimum size
        if radius > 10:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            cv.circle(frame, center, 5, (0, 0, 255), -1)
 
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
        cv.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
        # print(pts[i - 1], " ", pts[i])
    return (fdX, fdY, pts, direction, cx, cy)

def depth_map(imgL, imgR):
    """ Depth map calculation. Works with SGBM and WLS. Need rectified images, returns depth map ( left to right disparity ) """
    # SGBM Parameters -----------------
    window_size = 3  # wsize default 3; 5; 7 for SGBM reduced size image; 15 for SGBM full size image (1300px and above); 5 Works nicely

    left_matcher = cv.StereoSGBM_create(
        minDisparity=-1,
        numDisparities=5*16,  # max_disp has to be dividable by 16 f. E. HH 192, 256
        blockSize=window_size,
        P1=8 * 3 * window_size,
        # wsize default 3; 5; 7 for SGBM reduced size image; 15 for SGBM full size image (1300px and above); 5 Works nicely
        P2=32 * 3 * window_size,
        disp12MaxDiff=12,
        uniquenessRatio=10,
        speckleWindowSize=50,
        speckleRange=32,
        preFilterCap=63,
        mode=cv.STEREO_SGBM_MODE_SGBM_3WAY
    )
    right_matcher = cv2.ximgproc.createRightMatcher(left_matcher)
    # FILTER Parameters
    lmbda = 80000
    sigma = 1.3
    visual_multiplier = 6

    wls_filter = cv.ximgproc.createDisparityWLSFilter(matcher_left=left_matcher)
    wls_filter.setLambda(lmbda)

    wls_filter.setSigmaColor(sigma)
    displ = left_matcher.compute(imgL, imgR)  # .astype(np.float32)/16
    dispr = right_matcher.compute(imgR, imgL)  # .astype(np.float32)/16
    displ = np.int16(displ)
    dispr = np.int16(dispr)
    filteredImg = wls_filter.filter(displ, imgL, None, dispr)  # important to put "imgL" here!!!

    filteredImg = cv2.normalize(src=filteredImg, dst=filteredImg, beta=0, alpha=255, norm_type=cv2.NORM_MINMAX);
    filteredImg = np.uint8(filteredImg)

    return filteredImg

# MAIN PROGRAM LOOP
while (True):
    # grab the current frame
    _, leftFrame = left.read()
    _, rightFrame = right.read()

    # blur frame, and convert it to the HSV
    leftblurred = cv.GaussianBlur(leftFrame, (11, 11), 0)  
    rightblurred = cv.GaussianBlur(rightFrame, (11, 11), 0)
    lefthsv = cv.cvtColor(leftblurred, cv.COLOR_BGR2HSV)
    righthsv = cv.cvtColor(rightblurred, cv.COLOR_BGR2HSV) 

    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    leftmask = cv.inRange(lefthsv, greenLower, greenUpper)
    leftmask = cv.erode(leftmask, None, iterations=2)
    leftmask = cv.dilate(leftmask, None, iterations=2)

    rightmask = cv.inRange(righthsv, greenLower, greenUpper)
    rightmask = cv.erode(rightmask, None, iterations=2)
    rightmask = cv.dilate(rightmask, None, iterations=2)

    # find contours in the mask and initialize the current (x, y) center of the ball
    leftcnts = cv.findContours(leftmask.copy(), cv.RETR_EXTERNAL,
        cv.CHAIN_APPROX_SIMPLE)
    leftcnts = imutils.grab_contours(leftcnts)
    leftcenter = None

    rightcnts = cv.findContours(rightmask.copy(), cv.RETR_EXTERNAL,
        cv.CHAIN_APPROX_SIMPLE)
    rightcnts = imutils.grab_contours(rightcnts)
    rightcenter = None
    
    # Call function for left frame
    (ldX, ldY, lpts, ldirection, lx, ly) = trackedObjectXYcoord (leftFrame, leftcnts, ldX, ldY, lpts, ldirection)
    # show the movement deltas and the direction of movement on the frame
    cv.putText(leftFrame, ldirection, (10, 30), cv.FONT_HERSHEY_SIMPLEX,
    0.65, (0, 0, 255), 3)
    cv.putText(leftFrame, "x: {}, y: {}".format(lx, ly),
    (10, leftFrame.shape[0] - 10), cv.FONT_HERSHEY_SIMPLEX,
    0.65, (0, 0, 255), 1)
    
    # Call function for right frame
    (rdX, rdY, rpts, rdirection, rx, ry) = trackedObjectXYcoord (rightFrame, rightcnts, rdX, rdY, rpts, rdirection)
    # show the movement deltas and the direction of movement on the frame
    cv.putText(rightFrame, rdirection, (10, 30), cv.FONT_HERSHEY_SIMPLEX,
    0.65, (0, 0, 255), 3)
    cv.putText(rightFrame, "x: {}, y: {}".format(rx, ry),
    (10, rightFrame.shape[0] - 10), cv.FONT_HERSHEY_SIMPLEX,
    0.65, (0, 0, 255), 1)
            
    # show the frame to our screen
    cv.imshow("LeftFrame", leftFrame)
    cv.imshow("RightFrame", rightFrame)
    key = cv.waitKey(1) & 0xFF
    counter+=1

    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

# release the camera
left.release()
right.release()
# close all windows
cv.destroyAllWindows()
