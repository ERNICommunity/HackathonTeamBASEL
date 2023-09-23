from vilib import Vilib
from picarx import Picarx
from robot_hat import Buzzer, TTS, Music
import time
import paho.mqtt.client as mqtt
import json
from threading import Lock, Thread

last_command = 0

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("command")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    message_text = str(msg.payload.decode('utf-8'))
    print( msg.topic + " " + message_text)
    commands = json.loads( msg.payload.decode('utf-8'))

    with px_lock:
        global last_command
        for command in commands:
            operation = command['operation']

            if operation == 'set_speed':
                cmd_set_speed( command)
                last_command = time.time()
            elif operation == 'stop':
                cmd_stop()
            elif operation == 'set_direction':
                cmd_set_direction( command)
                last_command = time.time()
            elif operation == 'say':
                cmd_say( command)
            elif operation == 'play_song':
                play_song(command)
            else:
                print('Unknown command')

px = Picarx()
px_lock = Lock()
tts_robot = TTS()
# Vilib.detect_obj_parameter['setting_resolution'] = (640, 480)
# Vilib.camera_start(vflip=False,hflip=False)
# Vilib.display(local=False,web=True)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

def play_song(command):
    song = command['song']

    player = SoundPlayer(song)
    player.start()

class SoundPlayer(Thread):
    def __init__(self, song):
        self.song = song

    def run(self):
        match self.song:
            case 'entli':
                notes = [("Middle C", 1), ("Middle D", 1), ("Middle E", 1), ("Middle F", 1),
                        ("Middle G", 2),                  ("Middle G", 2),
                        ("Middle A", 1), ("Middle A", 1), ("Middle A", 1), ("Middle A", 1),
                        ("Middle G", 4),
                        ("Middle A", 1), ("Middle A", 1), ("Middle A", 1), ("Middle A", 1),
                        ("Middle G", 4),
                        ("Middle F", 1), ("Middle F", 1), ("Middle F", 1), ("Middle F", 1),
                        ("Middle E", 2),                  ("Middle E", 2),
                        ("Middle D", 1), ("Middle D", 1), ("Middle D", 1), ("Middle D", 1),
                        ("Middle C", 4)]
            case _:
                notes = [("Middle F", 1), ("Middle E", 1), ("Middle D#", 1),
                         ("Middle D", 3)]

        self.play(notes, tempo=120)

    def play(self, notes, tempo):
        m = Music()
        buzzer = Buzzer("P0")
        m.tempo(tempo)

        for note in notes:
            buzzer.play(m.note(note[0]), m.beat(note[1]))

def cmd_say( command):
    text = command['text']

    tts_robot.say( text)

def cmd_set_speed( cmd):
    speed = cmd['speed']

    if( speed > 0 & speed < 50):
        px.forward( speed)
    elif( speed < 0 & speed > -50):
        px.backward( -speed)
    else:
        px.stop()

def cmd_stop():
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

    if time.time() - last_command > 3000:
        cmd_stop()

    time.sleep( 0.2)
