#!/usr/bin/env python
import rospy
import getpass
from sensor_msgs.msg import JointState
import time
import math


def ang_vel(lvel, rvel):
    w = 0.0
    if ((lvel - rvel) != 0):
        v1 = float(lvel)
        v2 = float(rvel)
        r1 = (v1 * .25)/(v2-v1)
        w  = v1/r1
    return w

def callback(data):
    t_sec = data.header.stamp.secs
    t_nsec = data.header.stamp.nsecs
    lvel = data.velocity[0]
    rvel = data.velocity[1] 
    v = (lvel + rvel)/2
    w = ang_vel(lvel, rvel)
    first = f.read(1)
    print(str(t_sec) + '.' + str(t_nsec) + '\t\t' + str(v) +'\t\t'+ str(w) + '\t\t' + str(lvel) + '\t\t' + str(rvel) + '\n')
    f.write(str(t_sec) + '.' + str(t_nsec) + '\t\t' + str(v) + '\t\t' + str(w) + '\t\t' + str(lvel) +'\t\t'+ str(rvel) +'\n')
    #time.sleep(2/60)

def listener():
    rospy.init_node('listenprint', anonymous=True)
    rospy.Subscriber("joint_states", JointState, callback)
    rospy.spin()

if __name__== '__main__':
    compname = getpass.getuser()
    f = open("/home/"+ compname +"/catkin_ws/ros_colo_dataset/Robot1_Odometry.dat", "w+")
    f.write("# Time [sec] \t\t\t Velocity [m/s] \t\t Angular Velocity [rad/s]\t\tLeft Wheel Velocity\t\tRIght Wheel Velocity\n")
    listener()

