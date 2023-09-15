#include "ros/ros.h"
#include "std_msgs/String.h"
#include <math.h>  
#include "fiducial_msgs/FiducialTransform.h"
#include "fiducial_msgs/FiducialTransformArray.h"
#include <iomanip>

#include <iostream>
#include <fstream>
 
using namespace std;
#define PI 3.14159265

class ArucoRecorder{
  private:
    ros::Subscriber * pose_sub;
    void record_data(const fiducial_msgs::FiducialTransformArray::ConstPtr& msg);
  public:
    ArucoRecorder(ros::NodeHandle &nh);
    ~ArucoRecorder()
    {
        cout << "Destructor called" <<endl; 
    }
};


void ArucoRecorder::record_data(const fiducial_msgs::FiducialTransformArray::ConstPtr& msg)
{
  ofstream meas_file;
  ofstream odo_file, gt_file;
  meas_file.open("/home/lemur-robot2/catkin_ws/ros_colo_dataset/Robot2_Measurement_x.dat", ofstream::app);
  for (int i=0; i<msg->transforms.size(); i++) {
    const fiducial_msgs::FiducialTransform &ft = msg->transforms[i];
    
    int id = ft.fiducial_id;
    float x_pos = ft.transform.translation.x;
    float y_pos = ft.transform.translation.y;
    float z_pos = ft.transform.translation.z;
    
    float range = sqrt(pow(x_pos, 2) + pow(z_pos, 2)); 
    float bearing = atan2(z_pos, x_pos)-PI/2;

    ROS_INFO("##Object ID: [%d]##", id);
    ROS_INFO("Range: [%f]", range);
    ROS_INFO("Bearing: [%f]", bearing);
    ROS_INFO("***************");

    meas_file << fixed << setprecision(4) << ros::Time::now() << "\t" << id << "\t\t" << range << "\t\t" << bearing << "\n";
 
  }
  meas_file.close();
  odo_file.close();
  gt_file.close();
}


ArucoRecorder::ArucoRecorder(ros::NodeHandle & nh){
  ROS_INFO("Aruco Record Started");
  ofstream meas_file;
  ofstream odo_file, gt_file;
  meas_file.open("/home/lemur-robot2/catkin_ws/ros_colo_dataset/Robot2_Measurement_x.dat");
  meas_file << "# time [sec]" << "\t\t" << "object id" << "\t" << "range [m]" << "\t" << "bearing [rad]" << "\n";
  meas_file.close();
  
  pose_sub = new ros::Subscriber(nh.subscribe<fiducial_msgs::FiducialTransformArray>("/fiducial_transforms_throttle", 1, &ArucoRecorder::record_data, this));
}


int main(int argc, char **argv)
{
  ros::init(argc, argv, "meas_record");
  ros::NodeHandle nh("~");
  
  ArucoRecorder * node = new ArucoRecorder(nh);

  ros::spin();
  
  return 0;
}
  
