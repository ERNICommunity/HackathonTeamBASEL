from vilib import Vilib
from picarx import Picarx
from robot_hat import TTS
import time
import paho.mqtt.client as mqtt
import json
from threading import Lock

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("command")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    message_text = str(msg.payload.decode('utf-8'));
    print( msg.topic + " " + message_text)
    commands = json.loads( msg.payload.decode('utf-8'))

    with px_lock:
        for command in commands:
            operation = command['operation']

            if  operation == 'set_speed':
                cmd_set_speed( command)
            elif operation == 'stop':
                cmd_stop( command)
            elif operation == 'set_direction':
                cmd_set_direction( command)
            elif operation == 'set_head_rotate':
                cmd_set_head_rotate( command)
            elif operation == 'set_head_tilt':
                cmd_set_head_tilt( command)
            elif operation == 'say':
                cmd_say( command)
            else:
                print('Unknown command')

px = Picarx()
px_lock = Lock()
tts_robot = TTS()
Vilib.camera_start(vflip=False,hflip=False)
Vilib.display(local=False,web=True)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

def cmd_say( command):
    text = command['text']

    tts_robot.say( text)


def cmd_set_head_tilt( cmd):
    angle = cmd['angle']

    if( -45 < angle & angle < 45):
        px.set_camera_servo2_angle( angle)

def cmd_set_head_rotate( cmd):
    angle = cmd['angle']

    if( -45 < angle & angle < 45):
        px.set_camera_servo1_angle( angle)

def cmd_set_speed( cmd):
    speed = cmd['speed']

    if( speed > 0 & speed < 50):
        px.forward( speed)
    elif( speed < 0 & speed > -50):
        px.backward( -speed)
    else:
        px.stop()

def cmd_stop( cmd):
    px.stop()

def cmd_set_direction( cmd):
    angle = cmd['angle']

    if( -45 < angle & angle < 45):
        px.set_dir_servo_angle( angle)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_start()

# separate mqtt client to send events and avoid threading issues
client2 = mqtt.Client()
client2.connect("localhost", 1883, 60)

while True:
    with px_lock:
        distance = round( px.ultrasonic.read(), 2)
        grayscale = px.get_grayscale_data()

    event = {
        "distance" : distance,
        "grayscale" : grayscale
    }

    client2.publish( "state", json.dumps( event))

    time.sleep( 0.2)
