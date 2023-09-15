#!/usr/bin/env python
import rospy
import getpass
from sensor_msgs.msg import JointState
import time
import math

def velocity(lvel, rvel):
    w = 0.0
    if ((lvel - rvel) != 0):
        v1 = float(lvel)
        v2 = float(rvel)
        r1 = (v2 * .24)/(v2-v1)
        w  = v2/r1
    return w

def callback(data):
    t_sec = data.header.stamp.secs
    t_nsec = data.header.stamp.nsecs
    lvel = data.velocity[0]
    rvel = data.velocity[1]
    v = (lvel + rvel)/2
    w = velocity(lvel, rvel)
    first = f.read(1)
    f.write(str(t_sec) + '.' + str(t_nsec) + '\t\t' + str(v) +'\t\t\t'+ str(w) +'\n')
    time.sleep(2/60)

def listener():
    rospy.init_node('listenprint', anonymous=True)
    rospy.Subscriber("joint_states", JointState, callback)
    rospy.spin()

if __name__== '__main__':
    compname = getpass.getuser()
    f = open("/home/"+ compname +"/catkin_ws/src/robot_controls/moveData.dat", "w+")
    f.write("Time(seconds)\t\t\tVelocity(m/s)\t\tAngular Velocity(ra/s)\n")
    listener()
