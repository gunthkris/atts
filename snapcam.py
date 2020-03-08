import cv2

camL = cv2.VideoCapture(0) # Cam L
camR = cv2.VideoCapture(1) # Cam R


cv2.namedWindow("Cam L")
cv2.namedWindow("Cam R")

img_counter = 0

while True:
    retL, frameL = camL.read()
    retR, frameR = camR.read()
    cv2.imshow("Cam L", frameL)
    cv2.imshow("Cam R", frameR)
    if not retL or not retR:
        break
    k = cv2.waitKey(1)

    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    elif k%256 == 32:
        # SPACE pressed
        img_name = "opencv_frameL_{}.png".format(img_counter)
        cv2.imwrite(img_name, frameL)
        print("{} written!".format(img_name))
        img_name = "opencv_frameR_{}.png".format(img_counter)
        cv2.imwrite(img_name, frameR)
        print("{} written!".format(img_name))
        
        img_counter += 1

cam.release()

cv2.destroyAllWindows()