"""
A simple script to connect a remote car and send controller inputs.
"""
# pylint: disable=E1101
import numpy as np
import sys, time, os
import pygame
import socket
import struct


if len(sys.argv) != 3:
    print("Usage: {:} <host> <port>".format(sys.argv[0]))
    sys.exit(1)
host = sys.argv[1]
port = int(sys.argv[2])
server_addr = (host, port)

pygame.init() 

# Set parameters and constants
size = width, height = 200, 100
FPS = 10
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DEADZONE = 0.15

if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    pygame.joystick.init()
    use_joystick = True
else:
    use_joystick = False

screen = pygame.display.set_mode(size)
pygame.display.set_caption("RPiCar Client")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(b'hiya', server_addr)

print('Connected to server')
print('Starting control loop')

while True:
    t0 = time.time()

    # Event loop    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  
            sys.exit()

    screen.fill(WHITE)

    if use_joystick:
        left_right = joystick.get_axis(0)
        front_back = -1.0 * joystick.get_axis(2)
    else:
        left_right = (
            pygame.key.get_pressed()[pygame.K_a] * -1.0 + 
            pygame.key.get_pressed()[pygame.K_d] * 1.0
        )
        front_back = (
            pygame.key.get_pressed()[pygame.K_DOWN] * -1.0 + 
            pygame.key.get_pressed()[pygame.K_UP] * 1.0
        )
    
    if abs(left_right) < DEADZONE:
        left_right = 0.0

    print('\r', end='')
    print(
        'Front/Back: {:.2f}    -    Left/Right: {:.2f}    '.format(front_back, left_right), 
        end=''
    )

    joy_input = struct.pack('>f', left_right) + struct.pack('>f', front_back)

    sock.sendto(joy_input, server_addr)

    pygame.display.flip()

    # Cap the FPS
    elapsed_time = time.time() - t0

    if ((1 / FPS) - elapsed_time) > 0:
        time.sleep((1 / FPS) - elapsed_time)
