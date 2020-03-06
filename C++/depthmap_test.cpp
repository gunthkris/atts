#include <string>
#include <iostream>
#include <opencv2/opencv.hpp>
#include "opencv2/core/core.hpp"
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/imgcodecs/imgcodecs.hpp"
#include "opencv2/highgui/highgui.hpp"
#include "opencv2/calib3d/calib3d.hpp"

using namespace std;
using namespace cv;

int main()
{
    VideoCapture leftCam(0);      //lets say 0 is left, 1 is right
    if (leftCam.isOpened() == false){cout << "error: Webcam connect unsuccessful\n";    return(0);    }
    VideoCapture rightCam(1);     //lets say 0 is left, 1 is right
    if (rightCam.isOpened() == false){cout << "error: Webcam connect unsuccessful\n";   return(0);    }
    Mat left, right;    
    Mat leftClone, rightClone;

char charCheckForEscKey = 0;

while (    charCheckForEscKey != 27 && leftCam.isOpened()  )
{

    leftCam.read(left);
    if (left.empty()){cout << "No frame to read" << endl;  break;}      
    leftClone = left.clone();               //copy from the left camera 
    imwrite("left.png", leftClone);         // write it to screenshot.png in this directory

    rightCam.read(right);
    if (right.empty()){cout << "No frame to read" << endl;  break;}     
    rightClone = right.clone();             //copy from the left camera 
    imwrite("right.png", rightClone);           // write it to screenshot.png in this directory

        Mat im_left = imread("left.png"); //left cam picture
        Mat im_right = imread("right.png"); // right cam  picture 

        Size imagesize = im_left.size();
        Mat disparity_left= Mat(imagesize.height,imagesize.width,CV_16S);
        Mat disparity_right=Mat(imagesize.height,imagesize.width,CV_16S);
        Mat g1,g2,disp,disp8;
        cvtColor(im_left,g1, COLOR_BGR2GRAY);
        cvtColor(im_right,g2, COLOR_BGR2GRAY);

        Ptr<cv::StereoBM> sbm =  StereoBM::create(16,21);

        sbm->setDisp12MaxDiff(1);
        sbm->setSpeckleRange(9);
        sbm->setSpeckleWindowSize(2);
        sbm->setUniquenessRatio(0);
        sbm->setTextureThreshold(507);
        sbm->setMinDisparity(-39);
        sbm->setPreFilterCap(61);
        sbm->setPreFilterSize(5);
        sbm->compute(g1,g2,disparity_left);

        normalize(disparity_left, disp8, 0, 255, NORM_MINMAX, CV_8U);
         namedWindow("Left", WINDOW_AUTOSIZE);
         imshow("Left", im_left);

        // namedWindow("Right", WINDOW_AUTOSIZE);
        // imshow("Right", im_right);
        namedWindow("Depth map", WINDOW_AUTOSIZE);
        imshow("Depth map", disp8);

        // namedWindow("Left Cloned", WINDOW_FREERATIO);
        // imshow("Left Cloned", leftClone);   // left is the left pic taken from camera 0

        charCheckForEscKey = waitKey(1);    
}

return(0);
}
