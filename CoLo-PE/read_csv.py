#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 23 14:36:28 2018

@author: william
"""

import getpass
import csv
from datetime import datetime
import math

compname = getpass.getuser()
datapath = "/home/"+ compname +"/full_tests/full_test_v3_6/"



def generate_robot_gt_file(robot_label):
    gt_file_name = "Robot"+ str(robot_label) + "_Groundtruth.dat"
    print(gt_file_name)
    f_r = open(datapath+gt_file_name, "w+")
    f_r.write("# Time [sec] \t\t\t x [m] \t\t y [m] \t\t orientation [rad]\n")
            
    input_data = list(csv.reader(open(datapath+"gt.csv", "r+")))
    num_rows = len(input_data)
    start_time = input_data[0][9]

    print("Experiment start time: ", start_time)
    dt_obj = datetime.strptime(start_time, "%Y-%m-%d %I.%M.%S.%f %p")
    time_tuple = dt_obj.timetuple()
    timestamp = dt_obj.timestamp()
    print(repr(timestamp))

    col_idx = 2
    while input_data[3][col_idx] != '':
        if input_data[3][col_idx] == 'irobot'+str(robot_label):
            break
        col_idx+=1

    row_idx = 7

    while row_idx < num_rows:
        cur_time = input_data[row_idx][1]
        x = input_data[row_idx][col_idx+3]
        tmp = input_data[row_idx][col_idx+5]  #z-positon(csv) -> y-position(dat)
        y_rot = input_data[row_idx][col_idx]
        if x!='':
            y = float(tmp)*-1
            x = float(x)
            if float(cur_time) >= 10:
                pitch = math.radians(float(y_rot))
                f_r.write(str(float(cur_time)+timestamp) + '\t\t' + str(x) + '\t\t' + str(y) + '\t\t'+ str(pitch) + '\n')
                
        row_idx+=1
        
    f_r.close()

def generate_landmarks_gt_file(landmark_names, landmarks_dict):
    gt_file_name = "Landmark_Groundtruth.dat"
    print(gt_file_name)
    f_r = open(datapath+gt_file_name, "w+")
    f_r.write("# Landmark_tags [sec] \t x [m] \t y [m] \n")

    input_data = list(csv.reader(open(datapath+"gt.csv", "r+")))
    num_rows = len(input_data)

    for landmark_name in landmark_names:
        col_idx = 2
        while input_data[3][col_idx] != '':
            if input_data[3][col_idx] == landmark_name:
                break
            col_idx+=1

        row_idx = 7

        while row_idx < num_rows:
            cur_time = input_data[row_idx][1]
            x = input_data[row_idx][col_idx+3]
            tmp = input_data[row_idx][col_idx+5]  #z-positon(csv) -> y-position(dat)
            if x!='' and float(cur_time) >= 10:
                tags = landmarks_dict.get(landmark_name)
                for tag_id in tags:
                    y = float(tmp)*-1
                    x = float(x)
                    print(str(landmark_name)+"\t"+str(tag_id) + "\t" + str(x) + "\t" + str(y))
                    f_r.write(str(tag_id) + "\t" + str(x) + "\t" + str(y) + '\n')
            
                break
            row_idx+=1
        
    f_r.close()



for robot_label in [1,2,3]:
    generate_robot_gt_file(robot_label)
    pass

landmark_names = ["landmark0", "landmark1", "landmark2", "landmark3", "landmark4", "landmark5", "landmark6", "landmark7"]
landmarks_dict = {"landmark0": [113, 114, 115, 116], "landmark1":[103, 104, 105, 106], "landmark2":[107], "landmark3":[110], "landmark4":[109], "landmark5":[108], "landmark6":[120],"landmark7":[124]}
generate_landmarks_gt_file(landmark_names, landmarks_dict)