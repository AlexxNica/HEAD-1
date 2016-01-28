#!/usr/bin/env python
import math

__author__ = 'tesfa'

import rospy
import rospkg
import json
from dynamic_reconfigure.server import Server
from faceshift_puppeteering.cfg import FBConfig
from faceshift_puppeteering.msg import FSValues
from faceshift_puppeteering.msg import FSShapekeys
from faceshift_puppeteering.msg import FSShapekey
from pau2motors.msg import pau
from blender_api_msgs.msg import Target
from blender_api_msgs.msg import AnimationMode
from pau2motors.MapperFactory import Quaternion2EulerYZX
from std_msgs.msg import Float32
from pau2motors.msg import pau


class faceshift_mapper():
    d = {}

    def __init__(self):
        self.parameters = {}
        # Current modes for publisher that could be combined by addition
        self.modes={
            'head_yaw': 1,
            'head_pitch': 2, # Currently not supprted by API to control yaw and pitch separately
            'head_roll': 4,
            'eyes': 8,
            'face': 16,
        }
        rospy.init_node("faceshift_puppeteering_mapper", anonymous = True)
        path = rospkg.RosPack().get_path('faceshift_puppeteering')
        shape_key_pairing = '%s/sophia/shapekey_pairing.json' % path
        global d
        with open(shape_key_pairing) as json_data:
            d = json.load(json_data)
        srv = Server(FBConfig, self.callback)
        rospy.Subscriber("/blender_api/faceshift_values", FSValues, self.publisher)

        self.pub_setter= rospy.Publisher('/blender_api/set_animation_mode', AnimationMode, queue_size=10)
        self.pub=rospy.Publisher('/blender_api/set_shape_keys', FSShapekeys, queue_size=10)
        self.pub_neck= rospy.Publisher('/blender_api/set_face_target', Target, queue_size=10)
        self.pub_head_rot = rospy.Publisher('/blender_api/set_head_rotation', Float32, queue_size=10)
        self.pub_gaze= rospy.Publisher('/blender_api/set_gaze_target', Target, queue_size=10)
        self.pub_pau = rospy.Publisher('/blender_api/set_pau', pau, queue_size=10)

        self.quoternion2euler = {
            'p': Quaternion2EulerYZX({'axis': 'x'}, None),
            'y': Quaternion2EulerYZX({'axis': 'y'}, None),
            'r': Quaternion2EulerYZX({'axis': 'z'}, None),
        }
        rospy.spin()

    def callback(self, config, level):
        self.parameters = config
        return config

    def publisher(self,shapekeys):
        '''
        :param shapekeys: Holds the values of the FSSvalue which holds the head pose(translation and rotation(in quatrenion) and eye_left and right with vector3 data for gaze and FSShapekeys to hold
         the blendhsape values from the system.
        :return:
        '''
        dict_shape={}


        b= AnimationMode()

        head_pau = pau()
        head_pau.m_headRotation = shapekeys.head_pose.orientation
        head_pau.m_eyeGazeLeftPitch = shapekeys.eye_left.x
        head_pau.m_eyeGazeLeftYaw = shapekeys.eye_left.y
        head_pau.m_eyeGazeRightPitch = shapekeys.eye_right.x
        head_pau.m_eyeGazeRightYaw = shapekeys.eye_right.y

        # For iterating over the shapekeys
        for i in shapekeys.keys.shapekey:
            dict_shape[i.name]= i.value

        if (bool(self.parameters)):
            for i in d:
                fshift_name = i
                pub_shape= FSShapekey()

                value = 0
                name= i.replace("-","").replace(".","")
                values= self.parameters['groups']['groups'][name]['parameters']

                #Check a list of items.
                if bool(values):
                    #pub_shape.name= fshift_name

                    for parameter in values:
                        sk= parameter.replace(name+"_","")
                        # this below doesn't work as it is the past values. The current values is
                        # value = value + (values[parameter]) * dict_shape[sk]
                        # if 'JAW' in fshift_name:
                           # rospy.loginfo(values[parameter])
                        value = value + (self.parameters[parameter]) * dict_shape[sk]
                    head_pau.m_shapekeys.append(fshift_name)
                    head_pau.m_coeffs.append(max(0,min(1,value)))
        else:
            rospy.loginfo("Problem")

        self.pub_pau.publish(head_pau)

if __name__ == "__main__":
    mapper= faceshift_mapper()
