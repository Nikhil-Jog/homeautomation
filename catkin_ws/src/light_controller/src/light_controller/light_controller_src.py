import rospy
from std_msgs.msg import Float32, Bool, String, Int32
import ast
import json
from time import time
import requests

current_light = [0, 0]
current_devices = None 

zone_presence = [0, 0]
min_sensor_brightness = 50
hz = 10
light_rate = -5.0/hz    #per second
target_brightness = 254

def set_light(lights, state, brightness):
    ip = "http://10.0.0.85/api/"
    username = "aX7y2eDnFfLiUgxbr4SUxybQ96iLlb7fASQMO2Pz"
    base_addr = ip + username + "/lights/{}/state"
    for i in range(len(lights)):
        req = json.dumps({'on':state, 'bri':int(brightness)})
        addr = base_addr.format(lights[i]);
        r = requests.put(addr, req);

def light1_callback(data):
    global current_light
    current_light[0] = data.data
    return

def light2_callback(data):
    global current_light
    current_light[1] = data.data
    return

def devices_callback(data):
    global current_devices
    current_devices = json.loads(data.data)

def zone2_callback(data):
    global zone_presence
    zone_presence[1] = data.data

def zone1_callback(data):
    global zone_presence
    zone_presence[0] = data.data

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

def dark_feedback_callback(data):
    global target_brightness
    global light_rate
    global min_sensor_brightness
    global current_light
    min_sensor_brightness = target_brightness + 10
    target_brightness = target_brightness + 50
    light_rate = light_rate * 0.75
    
    rospy.loginfo('Feedback Received: Too Dark. New Target: {}, New Rate: {}, New Min: {}'.format(target_brightness, light_rate, min_sensor_brightness))


def weather_update_callback(data):
    global current_light
    global light_rate
    rate = light_rate
    weather = data.data #data = 0 -> !Cloudy, data = 1 -> Cloudy
    if (current_light > 200):
        if (weather == 0):
            rate = -abs(rate)
        else:
            rate = abs(rate)
    else:
        if (weather == 1):
            rate = abs(rate) * 2
        else:
            rate = -abs(rate)

    rospy.loginfo('Weather Update: {}. Old Rate: {}, New Rate: {}'.format(weather, light_rate, rate))
    light_rate = rate

def collect_data():
    global current_light
    global zone_presence
    global min_sensor_brightness
    global light_rate
    global target_brightness

    zone1_lights = ["2", "3", "4"];
    zone2_lights = ["1"];
    zone_lights = [zone1_lights, zone2_lights]
        
    hue = 300;
    hz = 10
    rate = rospy.Rate(hz)

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
                # if (current_light[i] < min_sensor_brightness):
                set_light(zone_lights[i], True, target_brightness)
                zone_published[i] = False;

            elif ((motion_timer[i] - ctime) > motion_off_timeout):
                motion_timer[i] = ctime + motion_off_timeout
        # Check for timeouts
        for i in xrange(len(motion_timer)):
            if ((ctime > motion_timer[i]) and (not zone_published[i])):
                set_light(zone_lights[i], False, 0)
                zone_published[i] = True;
            if (not zone_published[i]):
                light_pubs[i].publish(int(target_brightness))
            else:
                light_pubs[i].publish(0)
        
        if (any(zone_presence)):
            target_brightness = min(max(target_brightness + light_rate, min_sensor_brightness), 254)
            if (target_brightness >= 254):
                light_rate = -1.0/10
        rate.sleep()


def light_controller_main():
    rospy.init_node('light_controller', anonymous=True)
    rospy.Subscriber("/pi/light1", Float32, light1_callback)
    rospy.Subscriber("/pi/light2", Float32, light2_callback)
    rospy.Subscriber("/router/devices", String, devices_callback)
    rospy.Subscriber('/pi/zone2', Int32, zone2_callback)
    rospy.Subscriber('/pi/zone1', Int32, zone1_callback)

    rospy.Subscriber('/feedback/dark', Int32, dark_feedback_callback)
    rospy.Subscriber('/feedback/weather', Int32, weather_update_callback)

    collect_data()