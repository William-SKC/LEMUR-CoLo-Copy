#!/usr/bin/env python
# license removed for brevity
import numpy as np
import rospy
import sys, termios, tty
import random
from math import radians, degrees
from ca_msgs.msg import Bumper
import getpass
import time
from geometry_msgs.msg import Twist


class create2_motion_controller(object):
    """
    docstring for create2_motion_controller

    note: improve evasion to be smarter
          make manual (optional)


    """
    def __init__(self):
        self.control_pub = rospy.Publisher("cmd_vel", Twist, queue_size = 30)
        self.state_sub = rospy.Subscriber("bumper", Bumper, self.robot_motion) #original_freq = 10hz
        self.rate = rospy.Rate(10)
        self.eva = False
        #not sure for get_param
        #self.lin = rospy.get_param('~linVel', .2)
        #self.ang = rospy.get_param('~angVel', 1.0)
        self.lin = 0.1
        self.ang = 0.4
        self.evasion_time = 0
        self.end_node = time.time() + (60 * 5)
        self.compname = getpass.getuser()
        self.f = open("/home/"+ self.compname +"/catkin_ws/ros_colo_dataset/Robot1_Odometry_c"+str(time.time())+".dat", "w+")
        self.f.write("# Time [sec] \t Velocity [m/s] \t Angular Velocity [rad/s] \n")
        self.movement_bindings = {
            'i':(1,0,0,0),
            'o':(1,0,0,-1),
            'j':(0,0,0,1),
            'l':(0,0,0,-1),
            'u':(1,0,0,1),
            ',':(-1,0,0,0),
            '.':(-1,0,0,1),
            'm':(-1,0,0,-1),
            }
        self.twist = Twist()

    def twist_msgs(self, lin_vel, ang_vel):
        rtime = time.time()
        self.f.write(str(rtime) + '\t\t' +str(lin_vel) + '\t\t' + str(ang_vel) + '\n')
        print(str(rtime) + '\t\t' +str(lin_vel) + '\t\t' + str(ang_vel) + '\n')

    def movements(self, key, linear, angular):
        x = self.movement_bindings[key][0]
        y = self.movement_bindings[key][1]
        z = self.movement_bindings[key][2]
        th = self.movement_bindings[key][3]
        twist = Twist()
        twist.linear.x = x*linear; twist.linear.y = y*linear; twist.linear.z = z*linear;
        twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = th*angular
        self.control_pub.publish(twist)

    def smooth_movements(self, linear_vel, angular_vel):

        '''
        control_input = [linear_vel, angular_vel]
        self.twist.linear.x = 0 # [pos: forward velocity
        self.twist.linear.y = 0 # no effects
        self.twist.linear.z = 0 # no effects
        self.twist.angular.x = 0  # no effects
        self.twist.angular.y = 0  # no effects
        self.twist.angular.z = 0.5 # angular velocity pos: counter-clock
        '''
        if 0.2 > linear_vel > 0:
            self.twist.linear.x = linear_vel
        elif linear_vel <= 0:
            self.twist.linear.x = 0
        else:
            self.twist.linear.x = 0.2

        if 0.1 > angular_vel > -0.1:
            self.twist.angular.z = angular_vel
        elif angular_vel > 0.1:
            self.twist.angular.z = 0.1
        else:
            self.twist.angular.z = -0.1

        self.twist.linear.x = 0.1
        self.twist.angular.z = 0


        self.twist_msgs(self.twist.linear.x, self.twist.angular.z)
        self.control_pub.publish(self.twist)


    def manual_control(self, manual_input):
        pass

    def backoff(self, barriers):
        print("backoff")
        linear_vel = self.twist.linear.x
        angular_vel = self.twist.angular.z

        linear_vel = (linear_vel-0.1)/2
        angular_vel = (angular_vel - 0.2)/2

        self.twist.linear.x = linear_vel
        self.twist.angular.z = angular_vel
        print("back 0: ", self.twist)
        self.control_pub.publish(self.twist)
        self.twist_msgs(self.twist.linear.x, self.twist.angular.z)        

        '''
        linear_vel = -0.1
        if barriers[0]: # barrier on the left:
            angular_vel = -0.2
        elif barriers[1]:
            angular_vel = -0.1
        elif barriers[2]:
            angular_vel = 0.2
        self.twist.linear.x = linear_vel
        self.twist.angular.z = angular_vel
        print("back 1: ", self.twist)
        self.control_pub.publish(self.twist)
        self.twist_msgs(self.twist.linear.x, self.twist.angular.z)
        '''
    def evasion(self, barriers):
        print("evasion")
        linear_vel = -0.1
        angular_vel = -0.2
        self.twist.linear.x = linear_vel
        self.twist.angular.z = angular_vel
        print("back 0: ", self.twist)
        self.control_pub.publish(self.twist)
        self.twist_msgs(self.twist.linear.x, self.twist.angular.z)

    def random_movement(self):
        print("Movement")
        delta_vel = random.uniform(-0.02, 0.02)
        delta_ang_vel = random.uniform(-0.07, 0.07)
        self.smooth_movements(self.twist.linear.x+delta_vel, self.twist.angular.z+delta_ang_vel)

    def robot_motion(self, data):
        if time.time() > self.end_node:
            exit()
        lef = data.is_light_left
        lefron = data.is_light_front_left
        lefcen =  data.is_light_center_left
        rigcen = data.is_light_center_right
        rigfron = data.is_light_front_right
        rig = data.is_light_right

        bumper_l = data.is_left_pressed
        bumper_r = data.is_right_pressed

        left_barrier = bumper_l | lefron
        front_barrier = lefcen | rigcen
        right_barrier =  rigfron  | bumper_r
        barriers = [left_barrier, front_barrier, right_barrier]
	#disabled rig and lef
        barriers_detected = lefron | lefcen | rigcen | rigfron | bumper_l | bumper_r
        if barriers_detected:
            self.backoff(barriers)
            self.evasion_time = time.time()+3
        elif self.evasion_time >= time.time():
            self.evasion(barriers)
        else:
            self.random_movement()

if __name__ == '__main__':
    rospy.init_node('create2_motion_controller', anonymous=True)
    c = create2_motion_controller()
    c.rate.sleep()
    rospy.spin()
