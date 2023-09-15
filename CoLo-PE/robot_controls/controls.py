#!/usr/bin/env python
from __future__ import print_function

import rospy
import sys, termios, tty
import time
import random
from math import radians, degrees
from ca_msgs.msg import Bumper
import getpass
from geometry_msgs.msg import Twist

movement_bindings = {
    'i':(1,0,0,0),
    'o':(1,0,0,-1),
    'j':(0,0,0,1),
    'l':(0,0,0,-1),
    'u':(1,0,0,1),
    ',':(-1,0,0,0),
    '.':(-1,0,0,1),
    'm':(-1,0,0,-1),
    }

welcomemsg = '''
Welcome!
If you wish to access autonomous control of the robot, then enter one.
If you wish to access manual control, enter two.
If you wish to leave, enter break.
'''
automsg = '''
If you want the robot to move in a square, type square.
If you want to see the robot move randomly, type random.
If you want to leave, type break.
'''
manualmsg = '''
The controls are like so, and all are lowercase.
u   i   o
j       l
m   ,   .
'''

class main(object):
    def __init__(self):
        self.lin = rospy.get_param('~linVel', .1)
        self.ang = rospy.get_param('~angVel', 1.0)
        self.compname = getpass.getuser()
        self.f = open("/home/"+ self.compname +"/catkin_ws/ros_colo_dataset/command_vel.dat", "w+")
        self.twist = Twist()

    def twist_msgs(self, lin_vel, ang_vel):
        linear = ang_vel
        angular = lin_vel
        rtime = time.time()
        self.f.write(str(rtime) + '\t\t' +str(linear) + '\t\t' + str(angular) + '\n')

    def publisher(self):
        pub = rospy.Publisher("cmd_vel", Twist, queue_size = 30)
        return pub

    def listener(self):
        rospy.Subscriber("Bumper", Bumper, self.callback)

    def key(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def movements(self, key, linear, angular):
        x = movement_bindings[key][0]
        y = movement_bindings[key][1]
        z = movement_bindings[key][2]
        th = movement_bindings[key][3]

        self.twist.linear.x = x*linear; self.twist.linear.y = y*linear; self.twist.linear.z = z*linear;
        self.twist.angular.x = 0; self.twist.angular.y = 0; self.twist.angular.z = th*angular
        pub = self.publisher()
        pub.publish(self.twist)
        self.twist_msgs(self.twist.linear.x, self.twist.angular.z)

    def callback(self, data):
        pass

    def square(self):
        sides = 4
        turns = 55
        forwards = 100
        for s in range(sides):
            for t in range(turns):
                self.movements('j', self.lin, 1.5)
                time.sleep(.1)
            for f in range(forwards):
                self.movements('i', self.lin, self.ang)
                time.sleep(.1) 
            

    def random(self, start, endTime):
        while True:
            keylist = ['u','i','o','u','i','o','j','l']
            rankey = random.choice(keylist)

            if rankey in ['j','l']:
                ranint = random.randint(2,30)
            else:
                ranint = random.randint(15,25)
            i = 0
            while i < ranint:
                movements(rankey, self.lin, self.ang)
                time.sleep(.1)
                i += 1
            if time.time() > start + endTime:
                break

    def manual(self):
        print(manualmsg)
        while True:
            k = self.key()
            if k in movement_bindings.keys():
                self.movements(k, self.lin, self.ang)
            if k == "b":
                break

if __name__ =="__main__":
    m = main()
    rospy.init_node('controls')
    m.publisher()
    m.square()
    rospy.spin()

    '''while True:
        input1 = raw_input(welcomemsg + "\n")

        if input1 == "one":
            input2 = raw_input("\n"+automsg+"\n")

            if input2 == "square":
                m.square()

            if input2 == "random":
                start = time.time()
                endTime = 15
                m.random(start, endTime)

            if input2 == "break":
                break

        if input1 == "two":
            m.manual()

        if input1 == "break":
            break'''
