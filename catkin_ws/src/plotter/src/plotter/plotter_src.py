import serial
from time import sleep, time
import sys
import rospy
from std_msgs.msg import Float32, Int32

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

z1 = [0, 0]
z2 = [0, 0]
w = [0, 0]
d = [0,0]
m = [0, 0]
l1 = [0,0]
l2 = [0,0]
r = [0,0]

fig,axes = plt.subplots(2,2)
lines = [[0,0], [0,0], [0,0,0], [0]]
lines[0][0], = axes[0][0].plot(z1, label='Zone 1')
lines[0][1], = axes[0][0].plot(z1, label='Zone 2')
lines[1][0], = axes[0][1].plot(z1, label='Weather Feedback')
lines[1][1], = axes[0][1].plot(z1, label='Darkness Feedback')
lines[2][0], = axes[1][0].plot(z1, label='Zone 1 Light')
lines[2][1], = axes[1][0].plot(z1, label='Zone 2 Light')
lines[2][2], = axes[1][0].plot(z1, label='Min Light')
lines[3][0], = axes[1][1].plot(z1, label='Rate of Change')

def animate(t):
    z1_t = z1[:]
    z2_t = z2[:]
    lines[0][0].set_data(range(len(z1_t)), z1_t)
    lines[0][1].set_data(range(len(z2_t)), z2_t)
    axes[0][0].set_xlim(0, len(z1_t))
    axes[0][0].set_ylim(-1, 4)
    axes[0][0].set_title('Occupancy Data')
    axes[0][0].legend()

    w_t = w[:]
    d_t = d[:]
    lines[1][0].set_data(range(len(w_t)), w_t)
    lines[1][1].set_data(range(len(d_t)), d_t)
    axes[0][1].set_xlim(0, len(w_t))
    axes[0][1].set_ylim(-1, 2)
    axes[0][1].set_title('Feedback')
    axes[0][1].legend()

    m_t = m[:]
    l1_t = l1[:]
    l2_t = l2[:]
    lines[2][0].set_data(range(len(l1_t)), l1_t)
    lines[2][1].set_data(range(len(l2_t)), l2_t)
    lines[2][2].set_data(range(len(m_t)), m_t)
    axes[1][0].set_xlim(0, len(m_t))
    axes[1][0].set_ylim(-1, 400)
    axes[1][0].set_title('Light')
    axes[1][0].legend()

    r_t = r[:]
    lines[3][0].set_data(range(len(r_t)), r_t)
    axes[1][1].set_xlim(0, len(r_t))
    axes[1][1].set_ylim(-2, 3)
    axes[1][1].set_title('Rate')
    axes[1][1].legend()

    return lines

ani=animation.FuncAnimation(fig, animate, frames=range(0,99999999,10000),
                            interval=10, blit=False, repeat=False)


def collect_data():
    rate = rospy.Rate(1)

    plt.show()
    while not rospy.is_shutdown():
        pass

def occupancy_z1_callback(data):
    z1.append(data.data)

def occupancy_z2_callback(data):
    z2.append(data.data)

def weather_callback(data):
    global d
    w.append(data.data)

    num_to_pad = len(w) - len(d)
    d = d + [0] * num_to_pad

def dark_callback(data):
    d.append(data.data)

def min_callback(data):
    m.append(data.data)

def l1_callback(data):
    l1.append(data.data)

def l2_callback(data):
    l2.append(data.data)

def r_callback(data):
    r.append(data.data)

def plotter_main():
    rospy.init_node('plotter', anonymous=True)
    rospy.Subscriber("/pi/zone1", Int32, occupancy_z1_callback)
    rospy.Subscriber("/pi/zone2", Int32, occupancy_z2_callback)
    rospy.Subscriber("/feedback/weather", Int32, weather_callback)
    rospy.Subscriber("/feedback/dark", Int32, dark_callback)
    rospy.Subscriber("/lc/min", Int32, min_callback)
    rospy.Subscriber("/lc/zone1", Int32, l1_callback)
    rospy.Subscriber("/lc/zone2", Int32, l2_callback)
    rospy.Subscriber("/lc/rate", Float32, r_callback)
    collect_data()
    
if __name__ == '__main__':
    plotter_main()

