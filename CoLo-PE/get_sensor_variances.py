# -*- coding: utf-8 -*-

import numpy as np
import sys
import getpass
from math import atan2, sqrt, pi
import statistics


def find_nearest_time_idx(l, value):
    if len(l) != 0:
        array = np.asarray(l)
        idx = (np.abs(array-value)).argmin()
        return idx
    else:
        return None

def find_next_time_idx(array, start_idx, value):
    i = start_idx
    try:
        array[i]
    except IndexError:
        i = -1
        return i
    while array[i] < value:
        i = i+1
        try:
            array[i]
        except IndexError:
            i = -1
            break
    return i

class DatasetAnalyzer:
    
    def __init__(self, name):
        self.name = name
    
    def create_landmark_map(self):
    	### Build landmark map  ###
        self.landmark_map = {}
        path=self.dataset_path + "Landmark_Groundtruth.dat"
        landmark_file=open(path,'r+');
        s = landmark_file.readline()
        while(s):
            if(s[0]!='#'):
               landmark_location = [float(s.split( )[1]), float(s.split( )[2])]
               self.landmark_map.update({int(s.split( )[0]): landmark_location})
            s = landmark_file.readline()
        landmark_file.close()
        print(self.landmark_map)
        #print "lm  ", self.landmark_map, "  lm"
        return self.landmark_map
            

    def getting_sensor_variances(self, dataset_path, dataset_labels, duration):
        self.dataset_path = dataset_path
        print("Absolute datapath: ")
        print(self.dataset_path)
        self.dataset_labels = dataset_labels
        self.create_landmark_map()

        self.num_robots = len(self.dataset_labels)
        self.diff_range_data = [[] for i in range(self.num_robots)]
        self.diff_bearing_data = [[] for i in range(self.num_robots)]
        self.diff_vel_data = [[] for i in range(self.num_robots)]
        self.diff_a_v_data = [[] for i in range(self.num_robots)]
        self.groundtruth_data = [[] for i in range(self.num_robots)]

        #self.groundtruth_time= [[] for i in range(self.num_robots)]
        self.time_arr = {'odometry': [[] for i in range(self.num_robots)], 'measurement': [[] for i in range(self.num_robots)], 'groundtruth': [[] for i in range(self.num_robots)]}

        #initialization for MRCLAMDatasets: put files into dictionaries:
        self.duration = duration # some more time to avoid index error
        self.start_time_arr = []
        #finding the starting time:
        for i, label in enumerate(self.dataset_labels):
            robot_num = str(label)
            groundtruth_path = self.dataset_path+"Robot"+robot_num+"_Groundtruth.dat"
            with open(groundtruth_path,'r+') as groundtruth_file:
                for line in groundtruth_file:
                    if str(line.split()[0]) != '#':
                        time = float(line.split()[0])
                        self.start_time_arr.append(time)
                        break
        self.start_time = max(self.start_time_arr)
        self.end_time = self.start_time + self.duration
        print('Staring time: ', self.start_time)
        #finding starting states:
        self.starting_states = {}
        for i, label in enumerate(self.dataset_labels):
            robot_num = str(label)
            groundtruth_path = self.dataset_path+"Robot"+robot_num+"_Groundtruth.dat"
            with open(groundtruth_path,'r+') as groundtruth_file:
                for line in groundtruth_file:
                    if line[0] != '#' and float(line.split()[0]) >= self.start_time:
                        time = round(float(line.split()[0]), 3)
                        x_pos = float(line.split()[1])
                        y_pos = float(line.split()[2])
                        orientation = float(line.split()[3])
                        self.starting_states[label] = [time, x_pos, y_pos, orientation]
                        break
        
    
        for i, label in enumerate(self.dataset_labels):
            robot_num = str(label)

            groundtruth_path = self.dataset_path+"Robot"+robot_num+"_Groundtruth.dat"
            with open(groundtruth_path,'r+') as groundtruth_file:
                for line in groundtruth_file:
                    if line[0] != '#' and (self.end_time >= float(line.split()[0]) >= self.start_time):
                        time = round(float(line.split()[0]), 3)
                        x_pos = float(line.split()[1])
                        y_pos = float(line.split()[2])
                        orientation = float(line.split()[3])
                        groundtruth_info = {'time':time, 'x_pos':x_pos, 'y_pos':y_pos, 'orientation':orientation}
                        self.groundtruth_data[i].append(groundtruth_info) 
                        self.time_arr['groundtruth'][i].append(time)


            meas_path = self.dataset_path+"Robot"+robot_num+"_Measurement_x.dat"
            with open(meas_path,'r+') as measure_file:
                for line in measure_file:
                    if line[0] != '#' and (self.end_time>= float(line.split()[0]) >= self.start_time):
                        time = round(float(line.split()[0]), 3)
                        subject_ID = int(line.split()[1])
                        measurment_range = float(line.split()[2])
                        bearing = float(line.split()[3])
                        
                        g_idx = find_nearest_time_idx(self.time_arr['groundtruth'][i],time) 
                        gt_x = self.groundtruth_data[i][g_idx]['x_pos']
                        gt_y = self.groundtruth_data[i][g_idx]['y_pos']
                        orientation = self.groundtruth_data[i][g_idx]['orientation']
                        landmark_loc = self.landmark_map.get(subject_ID)
                        if landmark_loc !=  None:
                            [lx, ly] = landmark_loc
                            range_hat = sqrt((lx-gt_x)*(lx-gt_x)+(ly-gt_y)*(ly-gt_y))
                            bearing_hat = (atan2((ly-gt_y), (lx-gt_x))-orientation)%pi
                            if abs(bearing_hat-pi) < abs(bearing_hat):
                                bearing_hat = bearing_hat-pi

                            diff_bearing = bearing - bearing_hat
                            diff_range = measurment_range- range_hat
                            self.diff_range_data[i].append(diff_range)
                            self.diff_bearing_data[i].append(diff_bearing)
                            self.time_arr['measurement'][i].append(time)
            
            
            odo_path = self.dataset_path+"Robot"+robot_num+"_Odometry.dat" 
            with open(odo_path,'r+') as odometry_file:
                lines = odometry_file.readlines()
                for line_idx in range(0, len(lines)):
                    line = lines[line_idx]
                    if line[0] != '#' and (self.end_time >= float(line.split()[0]) >= self.start_time):
                        t = float(line.split()[0])
                        time = round(float(line.split()[0]), 3)
                        g_idx = find_nearest_time_idx(self.time_arr['groundtruth'][i],time) 
                        velocity = float(line.split()[1])
                        a_v = float(line.split()[2])
                        orientation = self.groundtruth_data[i][g_idx]['orientation']
                        try:
                            next_line = lines[line_idx+1]
                            next_time = float(next_line.split()[0])
                            delta_t = next_time - time
                        except IndexError:
                            delta_t = 0
                        if delta_t < 0:
                            sys.exit('incorrect delta_t: '+ str(delta_t))

                        gt_t = self.groundtruth_data[i][g_idx]['time']
                        gt_x = self.groundtruth_data[i][g_idx]['x_pos']
                        gt_y = self.groundtruth_data[i][g_idx]['y_pos']

                        try:
                            gt_t_next = self.groundtruth_data[i][g_idx+5]['time']
                            gt_x_next = self.groundtruth_data[i][g_idx+5]['x_pos']
                            gt_y_next = self.groundtruth_data[i][g_idx+5]['y_pos']
                            distance = sqrt((gt_x_next-gt_x)*(gt_x_next-gt_x)+(gt_y_next-gt_y)*(gt_y_next-gt_y))
                            change_bearing = (atan2((gt_y_next-gt_y), (gt_x_next-gt_x))-orientation)%pi
                            if abs(change_bearing-pi) < abs(change_bearing):
                                change_bearing = change_bearing-pi
                            duration  = gt_t_next - gt_t

                        except IndexError:
                            gt_t_prev = self.groundtruth_data[i][g_idx-5]['time']
                            gt_x_prev = self.groundtruth_data[i][g_idx-5]['x_pos']
                            gt_y_prev = self.groundtruth_data[i][g_idx-5]['y_pos']
                            distance = sqrt((gt_x_prev-gt_x)*(gt_x_prev-gt_x)+(gt_y_prev-gt_y)*(gt_y_prev-gt_y))
                            change_bearing = (atan2((gt_y-gt_y_prev), (gt_x-gt_x_prev))-orientation)%pi
                            if abs(change_bearing-pi) < abs(change_bearing):
                                change_bearing = change_bearing-pi
                            duration  = gt_t - gt_t_prev
                        diff_vel = velocity - distance/duration

                        try:
                            gt_t_next = self.groundtruth_data[i][g_idx+15]['time']
                            gt_x_next = self.groundtruth_data[i][g_idx+15]['x_pos']
                            gt_y_next = self.groundtruth_data[i][g_idx+15]['y_pos']
                            distance = sqrt((gt_x_next-gt_x)*(gt_x_next-gt_x)+(gt_y_next-gt_y)*(gt_y_next-gt_y))
                            change_bearing = (atan2((gt_y_next-gt_y), (gt_x_next-gt_x))-orientation)%pi
                            if abs(change_bearing-pi) < abs(change_bearing):
                                change_bearing = change_bearing-pi
                            duration  = gt_t_next - gt_t

                        except IndexError:
                            gt_t_prev = self.groundtruth_data[i][g_idx-15]['time']
                            gt_x_prev = self.groundtruth_data[i][g_idx-15]['x_pos']
                            gt_y_prev = self.groundtruth_data[i][g_idx-15]['y_pos']
                            distance = sqrt((gt_x_prev-gt_x)*(gt_x_prev-gt_x)+(gt_y_prev-gt_y)*(gt_y_prev-gt_y))
                            change_bearing = (atan2((gt_y-gt_y_prev), (gt_x-gt_x_prev))-orientation)%pi
                            if abs(change_bearing-pi) < abs(change_bearing):
                                change_bearing = change_bearing-pi
                            duration  = gt_t - gt_t_prev
                        
                        diff_a_v = a_v - change_bearing/duration
                        self.diff_vel_data[i].append(diff_vel)
                        self.diff_a_v_data[i].append(diff_a_v)


                        self.time_arr['odometry'][i].append(time)

        
        range_vars = []
        bearing_vars = [] 
        velocity_vars = []
        angular_vel_vars = []
        for i, label in enumerate(self.dataset_labels):
            print("*****************")
            print('robot label: ', label)
            print('range mean: ', statistics.mean(self.diff_range_data[i]))
            range_var = statistics.variance(self.diff_range_data[i])
            range_vars.append(range_var)
            print('range variance: ', range_var)    

            print('bearing mean:', statistics.mean(self.diff_bearing_data[i])) 
            bearing_var = statistics.variance(self.diff_bearing_data[i])
            bearing_vars.append(bearing_var)
            print('bearing variance: ', bearing_var)
            
            print('velocity mean: ', statistics.mean(self.diff_vel_data[i]))
            velocity_var = statistics.variance(self.diff_vel_data[i])
            velocity_vars.append(velocity_var)
            print('velocity variance: ', velocity_var)    

            print('angular velocity mean:', statistics.mean(self.diff_a_v_data[i])) 
            angular_vel_var = statistics.variance(self.diff_a_v_data[i])
            angular_vel_vars.append(angular_vel_var)
            print('angular velocity variance: ', angular_vel_var)
        
        print("*******Sensor Variances**********")
        print("range \t\t bearing \t\t velocity \t\t angular velocity ")
        print(statistics.mean(bearing_vars), statistics.mean(range_vars), statistics.mean(velocity_vars), statistics.mean(angular_vel_vars))
        return  statistics.mean(bearing_vars), statistics.mean(range_vars), statistics.mean(velocity_vars), statistics.mean(angular_vel_vars)


compname = getpass.getuser()
dataset_path = "/home/"+ compname +"/full_tests/full_test_v3_6/"
dataset_labels = [1,2,3]
duration = 200 # duration for the simulation in sec
dataset = DatasetAnalyzer('DatasetAnalyzer')
dataset.getting_sensor_variances(dataset_path, dataset_labels, duration)