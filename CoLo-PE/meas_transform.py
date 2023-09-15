#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 23 15:45:39 2018

@author: william
"""

import getpass
import math

compname = getpass.getuser()

dataset_path = "/home/"+ compname +"/full_tests/full_test_v3_6/"

def meas_to_meas_x(robot_label):
    meas_x_file_name = "Robot"+str(robot_label)+"_Measurement_x.dat"
    print(meas_x_file_name)
    f = open(dataset_path+meas_x_file_name, "w+")
    f.write("# Time [sec] \t\t object id \t\t range [m] \t\t bearing [rad]\n")
    robot_r = 0.16 #distance between label and the center of the robot
    l = 0.1 #distance between cam and the center of the robot

    lable_dict = {}
    path=dataset_path + "robot_labels.dat"
    robot_labels=open(path,'r+');
    s = robot_labels.readline()
    while(s):
        if(s[0]!='#'):
           lable_dict.update({s.split( )[0]: s.split( )[1]})
        s = robot_labels.readline()
    robot_labels.close()

    meas_file_name = "Robot"+str(robot_label)+"_Measurement.dat"
    with open(dataset_path+meas_file_name,'r+') as measure_file:
        for line in measure_file:
            if line[0] != '#':
                subject_ID = line.split()[1]
                range_cam = float(line.split()[2])
                bearing = float(line.split()[3])
                robot_id = lable_dict.get(subject_ID)
                if robot_id != None:
                    subject_ID = robot_id
                    range_cam = range_cam+robot_r
                
                phi = math.atan2((range_cam*math.sin(bearing)), (range_cam*math.cos(bearing)+l))
                if phi != 0:
                    r_cen = range_cam*math.sin(bearing)/math.sin(phi)
                f.write(line.split()[0] + '\t' + subject_ID + '\t\t\t' + str(r_cen) + '\t\t\t'+ str(phi) +'\n')
            
    f.close()

for robot_label in [1,2,3]:
    meas_to_meas_x(robot_label)