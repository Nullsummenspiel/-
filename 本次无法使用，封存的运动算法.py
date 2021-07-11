#!/usr/bin/env python

from __future__ import print_function
import numpy as np
from numpy.lib.function_base import angle
from numpy.lib.scimath import arcsin, sqrt
import roslib; roslib.load_manifest('teleop_twist_keyboard')
import roslib; roslib.load_manifest('teleop_twist_keyboard')
import rospy

from geometry_msgs.msg import Twist

import sys, select, termios, tty

msg = """
Reading from the keyboard  and Publishing to Twist!
---------------------------
Moving around:
   u    i    o         ^
   j    k    l       < v >
   m    ,    .

For Holonomic mode (strafing), hold down the shift key:
---------------------------
   U    I    O
   J    K    L
   M    <    >

t : up (+z)
b : down (-z)

anything else : stop

q/z : increase/decrease max speeds by 10%
w/x : increase/decrease only linear speed by 10%
e/c : increase/decrease only angular speed by 10%

CTRL-C to quit
"""

moveBindings = {
        'i':(1,0,0,0),
        'o':(1,0,0,-1),
        'j':(0,0,0,1),
        'l':(0,0,0,-1),
        'u':(1,0,0,1),
        ',':(-1,0,0,0),
        '.':(-1,0,0,1),
        'm':(-1,0,0,-1),
        'O':(1,-1,0,0),
        'I':(1,0,0,0),
        'J':(0,1,0,0),
        'L':(0,-1,0,0),
        'U':(1,1,0,0),
        '<':(-1,0,0,0),
        '>':(-1,-1,0,0),
        'M':(-1,1,0,0),
        't':(0,0,1,0),
        'k':(0,0,0,0),
        ' ':(0,0,0,0),
        'b':(0,0,-1,0),
        'A':(1,0,0,0),
        'B':(-1,0,0,0),
        'C':(0,0,0,-1),
        'D':(0,0,0,1),
    }

speedBindings={
        'q':(1.1,1.1),
        'z':(.9,.9),
        'w':(1.1,1),
        'x':(.9,1),
        'e':(1,1.1),
        'c':(1,.9),
    }

def getKey():
    tty.setraw(sys.stdin.fileno())
    select.select([sys.stdin], [], [], 0)
    key = sys.stdin.read(1)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


def vels(speed,turn):
    return "currently:\tspeed %s\tturn %s " % (speed,turn)

if __name__=="__main__":
    settings = termios.tcgetattr(sys.stdin)

    pub = rospy.Publisher('cmd_vel', Twist, queue_size = 1)
    rospy.init_node('teleop_twist_keyboard')

    speed = rospy.get_param("~speed", 0.5)
    turn = rospy.get_param("~turn", 1.0)
    x = 0
    y = 0
    z = 0
    th = 0
    status = 0
    x_i = 0.0
    y_i = 0.0
    angle_i = 0.0
    angle_last = 0.0
    fangxiang=0
    runtime = 0.0
    runtime_line = 0.0
    turn_angle = 0.0
    max_turn = 2.5
    min_turn = 1.5
    radius = 0.0
    file_path = '/home/xtark/zuobiao.txt'
    zuobiao = []
    with open(file_path) as file_object:
        for line in file_object:
            line_list = line.split()
            zuobiao_linshi = map(eval, line_list)
            zuobiao_linshi = list(zuobiao_linshi)
            zuobiao.append(zuobiao_linshi)
    zuobiao = np.array(zuobiao)
    length = zuobiao.shape
    i_list = length[0]
    try:
        print(msg)
        print(vels(speed,turn))
        while(1):
            '''
            key = getKey()
            #print("%s"%(key))
            if key in moveBindings.keys():
                x = moveBindings[key][0]
                y = moveBindings[key][1]
                z = moveBindings[key][2]
                th = moveBindings[key][3]
                twist = Twist()
                twist.linear.x = x*speed; twist.linear.y = y*speed; twist.linear.z = z*speed;
                twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = th*turn
                pub.publish(twist)
            elif key in speedBindings.keys():
                speed = speed * speedBindings[key][0]
                turn = turn * speedBindings[key][1]

                print(vels(speed,turn))
                if (status == 14):
                    print(msg)
                status = (status + 1) % 15
            else:
                x = 0
                y = 0
                z = 0
                th = 0
                if (key == '\x03'):
                    break
            '''
            for i in range(0,i_list):
                x_i = zuobiao[i+1,0]-zuobiao[i,0]
                y_i = zuobiao[i+1,1]-zuobiao[i,1]
                angle_i = np.arctan(y_i/x_i)
                if angle_i == angle_last and x_i > 0:
                    distance = sqrt(y_i*y_i+x_i*x_i)
                    runtime = distance/speed
                    linearspeed = 1
                    fangxiang = 0
                else:
                    distance = sqrt(y_i*y_i+x_i*x_i)
                    
                    if distance > max_turn:
                        go_angle = np.pi-abs(angle_i)-arcsin(abs(x_i)*np.sin(abs(angle_i))/max_turn)
                        go_distance = max_turn*np.sin(go_angle)/np.sin(angle_i)
                        runtime_line = (distance-max_turn)/speed
                        distance = max_turn
                        x_i = x_i/abs(x_i)*max_turn*np.cos(go_angle)
                        y_i = y_i/abs(y_i)*max_turn*np.sin(go_angle)
                        angle_i = np.arctan(y_i/x_i)
                        linearspeed = 1
                        fangxiang = 0
                        ros_last_time = rospy.get_rostime()
                        ros_last_time = ros_last_time.to_nsec()
                        t = rospy.get_rostime()
                        t = t.to_nsec()
                        while(t/1000000000 < ros_last_time/1000000000 + runtime_line):
                            twist = Twist()
                            twist.linear.x = linearspeed*speed; twist.linear.y = 0; twist.linear.z = 0;
                            twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = fangxiang*turn
                            pub.publish(twist)
                            t = rospy.get_rostime()
                            t = t.to_nsec()
                        print(runtime_line)
                    if distance < min_turn:
                        go_angle = np.pi-abs(angle_i)-arcsin(x_i*np.sin(abs(angle_i))/min_turn)
                        go_distance = min_turn*np.sin(go_angle)/np.sin(angle_i)
                        runtime_line = (min_turn-distance)/speed
                        distance = min_turn
                        x_i = x_i/abs(x_i)*min_turn*np.cos(go_angle)
                        y_i = y_i/abs(y_i)*min_turn*np.sin(go_angle)
                        angle_i = np.arctan(y_i/x_i)
                        linearspeed = 1
                        fangxiang = 0
                        ros_last_time = rospy.get_rostime()
                        ros_last_time = ros_last_time.to_nsec()
                        t = rospy.get_rostime()
                        t = t.to_nsec()
                        while(t/1000000000 < ros_last_time/1000000000 + runtime_line):
                            twist = Twist()
                            twist.linear.x = linearspeed*speed; twist.linear.y = 0; twist.linear.z = 0;
                            twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = fangxiang*turn
                            pub.publish(twist)
                            t = rospy.get_rostime()
                            t = t.to_nsec()
                        print(runtime_line)
                    
                    if x_i > 0:
                        turn_angle = 2*(angle_i - angle_last)
                    if x_i < 0:
                        turn_angle = 2*(angle_i + np.pi - angle_last)
                    
                    if turn_angle > np.pi and turn_angle > 0:
                        turn_angle = turn_angle - 2*np.pi
                    if turn_angle < -np.pi and turn_angle < 0:
                        turn_angle = 2*np.pi + turn_angle
                    
                    if turn_angle > 0:
                        runtime = turn_angle/(turn*2/3)
                        fangxiang = 1
                        radius = distance/2/np.sin(turn_angle)
                        linearspeed = (turn*2/3)*abs(radius)/speed
                    if turn_angle < 0:
                        runtime = -turn_angle/(turn*2/3)
                        fangxiang = -1
                        radius = distance/2/np.sin(turn_angle)
                        linearspeed = (turn*2/3)*abs(radius)/speed
                ros_last_time = rospy.get_rostime()
                ros_last_time = ros_last_time.to_nsec()
                t = rospy.get_rostime()
                t = t.to_nsec()
                while(t/1000000000 < ros_last_time/1000000000 + runtime):
                    twist = Twist()
                    twist.linear.x = linearspeed*speed; twist.linear.y = 0; twist.linear.z = 0;
                    twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = fangxiang*turn
                    pub.publish(twist)
                    t = rospy.get_rostime()
                    t = t.to_nsec()
                print(runtime)
                print(turn_angle)
                angle_last = turn_angle

    except Exception as e:
        print(e)

    finally:
        twist = Twist()
        twist.linear.x = 0; twist.linear.y = 0; twist.linear.z = 0
        twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = 0
        pub.publish(twist)
        print("tui chu lo")
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
