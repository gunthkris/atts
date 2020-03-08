import cv2

camR = cv2.VideoCapture(0) # Cam R
camL = cv2.VideoCapture(1) # Cam L


cv2.namedWindow("Cam R")
cv2.namedWindow("Cam L")

img_counter = 5

while True:
    retR, frameR = camR.read()
    retL, frameL = camL.read()
    cv2.imshow("Cam R", frameR)
    cv2.imshow("Cam L", frameL)
    if not retR or not retL:
        break
    k = cv2.waitKey(1)

    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    elif k%256 == 32:
        # SPACE pressed
        img_name = "Image/opencv_frameR_{}.png".format(img_counter)
        cv2.imwrite(img_name, frameR)
        print("{} written!".format(img_name))
        img_name = "Image/opencv_frameL_{}.png".format(img_counter)
        cv2.imwrite(img_name, frameL)
        print("{} written!".format(img_name))
        
        img_counter += 1

cam.release()

cv2.destroyAllWindows()
