import serial
from time import sleep, time
import sys
import rospy
from std_msgs.msg import Float32, Int32

# configure the serial connections (the parameters differs on the device you are connecting to)
ser = serial.Serial(
    port='/dev/ttyACM0',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1,
)


def collect_data():
    light_pub = rospy.Publisher('/pi/light', Float32, queue_size=10)
    temp_pub = rospy.Publisher('/pi/temp', Float32, queue_size=10)
    zone2_pub = rospy.Publisher('/pi/zone2', Int32, queue_size=10)

    rospy.loginfo('Comms Init')

    while not rospy.is_shutdown():
        if (ser.inWaiting()):
            data = ser.readline().strip().split(' ')
            # rospy.loginfo(data)
            light_pub.publish(float(data[0]))
            temp_pub.publish(float(data[1]))
            zone2_pub.publish(int(data[2]))
        else:
            ser.write('D')

def comms_main():
    rospy.init_node('comms', anonymous=True)

    collect_data()
    
if __name__ == '__main__':
    comms_main()
