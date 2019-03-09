"""
A simple control loop that receives steering and throttle inputs from a remote machine
via UDP and uses the signals to control a car via the PCA968 interface.
"""
# pylint: disable=E1101
import numpy as np
import sys, time
# import pygame
import socket
import struct
import Adafruit_PCA968


if len(sys.argv) != 3:
    print("Usage: {:} <host> <port>".format(sys.argv[0]))
    sys.exit(1)
host = sys.argv[1]
port = int(sys.argv[2])
server_addr = (host, port)

# pygame.init()  

# Set parameters and constants
# size = width, height = 960, 480
# imsize = imwidth, imheight = 640, 480
FPS = 30
# WHITE = (255, 255, 255)
# BLACK = (0, 0, 0)

MIN_STEERING, MAX_STEERING = 300, 460   # Right to left
MIN_THROTTLE, MAX_THROTTLE = 320, 420   # Reverse to front


def get_steering_pwm(value):
    """
    Convert value [-1, 1] to the range [MIN_STEERING, MAX_STEERING]
    """
    return MIN_STEERING + (1 + (-1 * value)) * 0.5 * (MAX_STEERING - MIN_STEERING)


def get_throttle_pwm(value):
    """
    Convert value [-1, 1] to the range [MIN_STEERING, MAX_STEERING]
    """
    return MIN_THROTTLE + (1 + value) * 0.5 * (MAX_THROTTLE - MIN_THROTTLE)


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(server_addr)

print("Waiting for client connection...")

msg, addr = sock.recvfrom(4)

if msg != b'hiya':
    raise Exception("Something went wrong!")

print("Connected with {:}:{:}".format(addr[0], addr[1]))
print("Starting control loop")

while True:
    t0 = time.time()

    # Receive two float32s from the client, one per axis of control (steering then throttle)
    msg, addr = sock.recvfrom(8)
    if not msg:
        break
    left_right = struct.unpack('>f', msg[:4])[0]
    front_back = struct.unpack('>f', msg[4:])[0]

    left_right_pwm = get_steering_pwm(left_right)
    front_back_pwm = get_throttle_pwm(front_back)

    print('\r', end='')
    print(
        'Front/Back: {:.2f} ({:>3})   -    Left/Right: {:.2f}  ({:>3})  '.format(
            front_back, front_back_pwm, left_right, left_right_pwm
        ), 
        end=''
    )

    pwm = Adafruit_PCA9685.PCA9685()
    pwm.set_pwm_freq(60)
    pwm.set_pwm(0, 0, )
    pwm.set_pwm(1, 0, get_steering_pwm(left_right))  # Scale these to bounds

    # Cap the FPS
    elapsed_time = time.time() - t0

    if ((1 / FPS) - elapsed_time) > 0:
        time.sleep((1 / FPS) - elapsed_time)
