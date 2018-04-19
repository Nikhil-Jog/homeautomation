import requests
import json
from time import sleep, time
from bs4 import BeautifulSoup
import rospy

from std_msgs.msg import String

def get_devices():
    router_payload = \
    {
        'username' : 'admin',
        'password' : 'chrisjoshnikhil'
    }
    with requests.Session() as s:
        p = s.post('http://10.0.0.1/check.php', data=router_payload)
        r = s.get('http://10.0.0.1/connected_devices_computers.php');
    soup = BeautifulSoup(r.text, 'html.parser')
    devices = list(map(lambda x: x.u.text, soup.find_all(headers='host-name')[:-1]))
    rssi_vals = list(map(lambda x: x.text, soup.find_all(headers='rssi-level')[:-1]))
    return dict(zip(devices, rssi_vals))

def collect_data():
    router_pub = rospy.Publisher('/router/devices', String, queue_size=10)
    rate = rospy.Rate(0.5)

    while not rospy.is_shutdown():
        dev = get_devices()
        router_pub.publish(json.dumps(dev))
        rate.sleep()

def router_main():
    rospy.init_node('router', anonymous=True)
    while(1):
        # try:
        collect_data()
        # except Exception as ex:
            # rospy.loginfo(ex)
            # pass

if __name__ == '__main__':
    router_main()
