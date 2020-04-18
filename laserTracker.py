# import the necessary packages
from collections import deque
import numpy as np
import argparse
import cv2 as cv
import time
import sys
import imutils
import panTiltControl as ptc  # Our Pan and Tilt Controller

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-b", "--buffer", type=int, default=20,
                help="max buffer size")
args = vars(ap.parse_args())

# =Lower and upper boundaries of the "Green laser pointer
# (180, 255, 255) max values
# Laser Pointer
# greenLower = (37, 9, 215)
# greenUpper = (77, 77, 255)
greenLower = (37, 7, 215)
greenUpper = (65, 45, 245)
# Ball
# greenLower = (40, 125, 70)
# greenUpper = (70, 255, 170)

# initialize the list of tracked points, the frame counter,
# and the coordinate deltas
lpts = deque(maxlen=args["buffer"])
counter = 0
(ldX, ldY) = (0, 0)
(lx, ly) = (0, 0)
ldirection = ""
accuracy = 3  # Pixel accuracy (default = 2)
targetDetected = False

# Grab a reference to the video file
left = cv.VideoCapture(0, cv.CAP_V4L2)
# If we can't get images from both sources, error
if not left.isOpened():
    print("Can't opened the streams!")
    sys.exit(-9)

# Set framges per second
left.set(5, 30)

# Reduce resolution
maxFrameWidth = 640
cw = maxFrameWidth/2
maxFrameHeight = 480
ch = maxFrameHeight/2
left.set(cv.CAP_PROP_FRAME_WIDTH, maxFrameWidth)
left.set(cv.CAP_PROP_FRAME_HEIGHT, maxFrameHeight)

# allow the camera to warm up
time.sleep(2.0)


# Move Turret based on location of target and center it
def centerTarget(targetDetected, counter):
    if targetDetected and counter > 12:
        if not cw-accuracy <= lx <= cw+accuracy:
            if lx < cw:
                if lx+100 < cw:
                    ptc.pan.setMicroStep("Full Step")
                    ptc.pan.rotateCW()
                elif lx+50 < cw:
                    ptc.pan.setMicroStep("Half Step")
                    ptc.pan.rotateCW()
                elif lx+25 < cw:
                    ptc.pan.setMicroStep("Quarter Step")
                    ptc.pan.rotateCW()
                elif lx+12 < cw:
                    ptc.pan.setMicroStep("Eighth Step")
                    ptc.pan.rotateCW()
                else:
                    ptc.pan.setMicroStep("Sixteenth Step")
                    ptc.pan.rotateCW()
            else:
                if lx-100 > cw:
                    ptc.pan.setMicroStep("Full Step")
                    ptc.pan.rotateCCW()
                elif lx-50 > cw:
                    ptc.pan.setMicroStep("Half Step")
                    ptc.pan.rotateCCW()
                elif lx-25 > cw:
                    ptc.pan.setMicroStep("Quarter Step")
                    ptc.pan.rotateCCW()
                elif lx-12 > cw:
                    ptc.pan.setMicroStep("Eighth Step")
                    ptc.pan.rotateCCW()
                else:
                    ptc.pan.setMicroStep("Sixteenth Step")
                    ptc.pan.rotateCCW()
        if not ch-accuracy <= ly <= ch+accuracy:
            if ly < ch:
                ptc.tilt.rotateCW()
                # if ly+100 < ch:
                #     ptc.tilt.setMicroStep("Full Step")
                #     ptc.tilt.rotateCCW()
                # elif ly+50 < ch:
                #     ptc.tilt.setMicroStep("Half Step")
                #     ptc.tilt.rotateCCW()
                # elif ly+25 < ch:
                #     ptc.tilt.setMicroStep("Quarter Step")
                #     ptc.tilt.rotateCCW()
                # elif ly+12 < ch:
                #     ptc.tilt.setMicroStep("Eighth Step")
                #     ptc.tilt.rotateCCW()
                # else:
                #     ptc.tilt.setMicroStep("Sixteenth Step")
                #     ptc.tilt.rotateCCW()
            else:
                ptc.tilt.rotateCCW()
                # if ly-100 > ch:
                #     ptc.tilt.setMicroStep("Full Step")
                #     ptc.tilt.rotateCW()
                # elif ly-50 < ch:
                #     ptc.tilt.setMicroStep("Half Step")
                #     ptc.tilt.rotateCW()
                # elif ly-25 < ch:
                #     ptc.tilt.setMicroStep("Quarter Step")
                #     ptc.tilt.rotateCW()
                # elif ly-12 < ch:
                #     ptc.tilt.setMicroStep("Eighth Step")
                #     ptc.tilt.rotateCW()
                # else:
                #     ptc.tilt.setMicroStep("Sixteenth Step")
                #     ptc.tilt.rotateCW()
    else:
        print("No target")


def detectTargetXYcoord(frame, cnts, fdX, fdY, pts, direction):
    # Set default (x, y) position if no target on screen
    (cx, cy) = (0, 0)
    targetDetected = False
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

        targetDetected = True

        # only proceed if the radius meets a minimum size
        if radius > 5:
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

        # otherwise, compute the thickness of the line and draw the connecting lines
        thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
        cv.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
    return (fdX, fdY, pts, direction, cx, cy, targetDetected)


# MAIN PROGRAM LOOP
while (True):
    # grab the current frame
    _, leftFrame = left.read()

    # blur frame, and convert it to the HSV
    leftblurred = cv.GaussianBlur(leftFrame, (11, 11), 0)
    lefthsv = cv.cvtColor(leftblurred, cv.COLOR_BGR2HSV)

    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    leftmask = cv.inRange(lefthsv, greenLower, greenUpper)
    leftmask = cv.erode(leftmask, None, iterations=2)
    leftmask = cv.dilate(leftmask, None, iterations=2)

    # find contours in the mask and initialize the current (x, y) center of the laser
    leftcnts = cv.findContours(leftmask.copy(), cv.RETR_EXTERNAL,
                               cv.CHAIN_APPROX_SIMPLE)
    leftcnts = imutils.grab_contours(leftcnts)
    leftcenter = None

    # Call function for left frame
    (ldX, ldY, lpts, ldirection, lx, ly, targetDetected) = detectTargetXYcoord(
        leftFrame, leftcnts, ldX, ldY, lpts, ldirection)

    # Show the movement deltas and the direction of movement on the frame
    # If a target has been detected
    if targetDetected:
        # print("With detection: {}, {}".format(lx, ly))
        targetText = "Target Detected"
    else:
        # print("Without detection: {}, {}".format(lx, ly))
        targetText = "Target Lost"
    cv.putText(leftFrame, ldirection, (10, 30), cv.FONT_HERSHEY_SIMPLEX,
               0.65, (0, 0, 255), 3)
    cv.putText(leftFrame, "x: {}, y: {} {}".format(lx, ly, targetText),
               (10, leftFrame.shape[0] - 10), cv.FONT_HERSHEY_SIMPLEX,
               0.65, (0, 0, 255), 1)

    # Center the target
    centerTarget(targetDetected, counter)

    # show the frame to our screen
    cv.imshow("LeftFrame", leftFrame)

    # if the 'q' key is pressed, stop the loop
    key = cv.waitKey(1) & 0xFF
    if key == ord("q"):
        break

    counter += 1

# release the camera
left.release()
# close all windows
cv.destroyAllWindows()
