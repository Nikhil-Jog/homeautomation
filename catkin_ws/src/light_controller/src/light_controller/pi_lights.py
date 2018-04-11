import serial
import rospy
from std_msgs.msg import Float32, Bool, String
import ast

def light_callback(data):
    rospy.loginfo(data)

def devices_callback(data):
    rospy.loginfo(ast.literal_eval(data))

def collect_data():
    rate = rospy.Rate(2)

    while not rospy.is_shutdown():
        rate.sleep()

def main():
    rospy.init_node('light_controller', anonymous=True)
    rospy.Subscriber("/pi/light", Float32, light_callback)
    rospy.Subscriber("/router/devices", String, devices_callback)
    while(1):
        try:
            collect_data()
        except Exception as ex:
            rospy.loginfo(ex)
            pass
