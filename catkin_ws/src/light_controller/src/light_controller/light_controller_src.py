import rospy
from std_msgs.msg import Float32, Bool, String, Int32
import ast
import json
from time import time
import requests

current_light = [0, 0]
current_devices = None 

zone_presence = [1, 0]

def set_light(lights, state, brightness):
    ip = "http://10.0.0.85/api/"
    username = "aX7y2eDnFfLiUgxbr4SUxybQ96iLlb7fASQMO2Pz"
    base_addr = ip + username + "/lights/{}/state"
    for i in range(len(lights)):
        req = json.dumps({'on':state, 'bri':brightness})
        addr = base_addr.format(lights[i]);
        r = requests.put(addr, req);

def light_callback(data):
    global current_light
    current_light[0] = data.data
    return

def devices_callback(data):
    global current_devices
    current_devices = json.loads(data.data)

def zone2_callback(data):
    global zone_presence
    zone_presence[1] = data.data

def RSS_override():
    global current_devices

    user_devices = [u'Galaxy-Note8', u'OnePlus_3T', u'DESKTOP-NTB0KRK', u'Macbook']
    RSS_Threshold = -60

    override = False
    for i in range(len(user_devices)):
        try:
            RSS = int(current_devices[user_devices[i]].split(' ')[0])
            if (RSS < RSS_Threshold):
                override = True
                break
        except Exception as ex:
            pass
    return override

def collect_data():
    global current_light
    global zone_presence

    zone1_lights = ["2", "3", "4"];
    zone2_lights = ["1"];
    zone_lights = [zone1_lights, zone2_lights]

    min_brightness = 250

    target_brightness = 254;
    min_sensor_brightness = 200
    on_state = True;
    saturation = 254
    hue = 300;
    rate = rospy.Rate(10)

    motion_timeout = [0, 0]
    motion_timer = [int(time()), int(time())]
    motion_off_timeout = 5
    motion_on_timeout = 86400

    zone_published = [False, False]

    rospy.loginfo('Light Controller Init')

    light_pubs = [rospy.Publisher('/lc/zone1', Int32, queue_size=10), rospy.Publisher('/lc/zone2', Int32, queue_size=10)]

    while not rospy.is_shutdown():
        ctime = int(time())
        # Check for motion
        for i in xrange(len(zone_presence)):
            if (zone_presence[i]):
                motion_timer[i] = ctime + motion_on_timeout
                if (current_light[i] < min_sensor_brightness):
                    set_light(zone_lights[i], True, target_brightness)
                    zone_published[i] = False;

            elif ((motion_timer[i] - ctime) > motion_off_timeout):
                motion_timer[i] = ctime + motion_off_timeout
        # Check for timeouts
        for i in xrange(len(motion_timer)):
            if ((ctime > motion_timer[i]) and (not zone_published[i])):
                set_light(zone_lights[i], False, 0)
                zone_published[i] = True;
            light_pubs[i].publish(not zone_published[i])
        # rospy.loginfo(str(motion_timer[1] - ctime))
        rate.sleep()

def light_controller_main():
    rospy.init_node('light_controller', anonymous=True)
    rospy.Subscriber("/pi/light", Float32, light_callback)
    rospy.Subscriber("/router/devices", String, devices_callback)
    rospy.Subscriber('/pi/zone2', Int32, zone2_callback)

    collect_data()