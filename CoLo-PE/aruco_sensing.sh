#!/bin/bash

cd $HOME/catkin_ws 
xterm -hold -e "roscore" &
xterm -hold -e "roslaunch usb_cam_stream_publisher.launch" &
sleep 5
xterm -hold -e "roslaunch aruco_markers_detect.launch" &
sleep 3
xterm -hold -e "rosrun image_view image_view image:=/fiducial_images" &
xterm -hold -e "rostopic echo /fiducial_transforms" &
sleep 2
xterm -hold -e "rosrun topic_tools throttle messages /fiducial_transforms 5.0" &
xterm -hold -e "rostopic hz fiducial_transforms_throttle"

cd $HOME/

exit 0

<<COMMENT
    For the throttle frequencies:
    Issues: throttle rates lower than expected(default rate = 30Hz)
	Expected rate [Hz]:     Real rate [Hz]:
	40			~30
	30			19.5~20
	20			~15
	15			~10.5
	10			~8.4
	8			~7.5
	4			~3.75
	1			0.98

COMMENT
