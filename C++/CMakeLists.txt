cmake_minimum_required(VERSION 3.10.2)
#project( FaceDetection2 )
find_package( OpenCV REQUIRED )
include_directories( ${OpenCV_INCLUDE_DIRS} )
#add_executable( FaceDetection facedetect2.cpp )
#target_link_libraries( FaceDetection ${OpenCV_LIBS} ) 

#project( ActiveTwoCam )
#add_executable( ActiveTwoCam ActiveTwoCam.cpp )
#target_link_libraries( ActiveTwoCam ${OpenCV_LIBS} ) 

project( DepthMap )
add_executable( DepthMap depthmap_test.cpp )
target_link_libraries( DepthMap ${OpenCV_LIBS} ) 
