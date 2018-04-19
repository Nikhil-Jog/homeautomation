import serial
from time import sleep, time
import sys
import rospy
from std_msgs.msg import Float32, Int32

ambient_light = [112.0, 112.0]


def ambient_light1_callback(data):
    global ambient_light
    if (data.data == 0):
        ambient_light[0] = 112.0
    else:
        ambient_light[0] = data.data

        if (data.data < 175 ):
            dark_pub = rospy.Publisher('/feedback/dark', Int32, queue_size=10)
            dark_pub.publish(1)

def ambient_light2_callback(data):
    global ambient_light
    if (data.data == 0):
        ambient_light[1] = 112.0
    else:
        ambient_light[1] = data.data

        if (data.data < 175):
            dark_pub = rospy.Publisher('/feedback/dark', Int32, queue_size=10)
            dark_pub.publish(1)

def mock_main():
    global ambient_light
    rospy.init_node('mock', anonymous=True)

    rospy.Subscriber("/lc/zone1", Int32, ambient_light1_callback)
    rospy.Subscriber("/lc/zone2", Int32, ambient_light2_callback)

    light_pub = [rospy.Publisher("/pi/light1", Float32, queue_size=10), rospy.Publisher("/pi/light2", Float32, queue_size=10)]
    zone_pub = [rospy.Publisher("/pi/zone1", Int32, queue_size=10), rospy.Publisher("/pi/zone2", Int32, queue_size=10)]
    weather_pub = rospy.Publisher('/feedback/weather', Int32, queue_size=10)

    zone_presence = [(0,0), (0,1), (0,0), (1,0), (0,0), (1,1), (0,0)]
    zone_timer    = [  0,     1,     15,    25,    35,    45,   180]

    weather_presence = [1, 0, 0]
    weather_timer = [55, 75, 180]

    rospy.loginfo('Mock Node Ready')
    rate = rospy.Rate(1)
    rate.sleep()
    time = 0
    idx = 0
    widx = 0
    while not rospy.is_shutdown():
        for i in xrange(len(ambient_light)):
            light_pub[i].publish(ambient_light[i])
        rospy.loginfo(time)
        if (time == zone_timer[idx]):
            zone_pub[0].publish(zone_presence[idx][0])
            zone_pub[1].publish(zone_presence[idx][1])
            idx = idx + 1

        if (time == weather_timer[widx]):
            weather_pub.publish(weather_presence[widx])
            widx = widx + 1
        time = time + 1
        rate.sleep()


    
if __name__ == '__main__':
    mock_main()
