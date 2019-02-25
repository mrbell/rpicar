# I'd like to try a simple test:
# Run a server that displays inputs and generates a set of random images
# Run a client that sends and displays inputs and displays images

# To start I'll just do this in a single app, i.e. I'll 
# capture input, display on screen, generate an image and 
# also show the image on screen.

# I will use pygame for input capture as well as to display 
# images to a GUI

# For an XBOne controller, 
#   Axis 0: left stick, left(-1) right (+1)
#   Axis 1: left stick, up(-1) down (+1)
#   Axis 2: left & right triggers, right (-1) left (+1)
#   Axis 3: right stick, up(-1) down(+1)
#   Axis 4: right stick, left(-1) right(+1)
#   Hat 0: (left(-1)/right(+1), up(+1)/down(-1))
#   Button 0, 1, 2, 3, 4, 5, 6, 7, 8, 9: A, B, X, Y, LB, RB, sel, start, left stick, right stick


## Sending controller inputs works great! 
## Sending images doesn't. Maybe I need separate sockets?
## TODO: Try creating another set of test client/server apps that just transmit the images
## and do not send controller stuff

## Maybe do something where the client connects to the server on port X with port Y. 
## It sends a UDP port A that the server should send stuff back on from port B.
## Then client would send controller inputs from port Y to server port X
## Server would send video from port B to client port A.

## I've played ith using PIL to compress using JPEG. I've found it reduces a random UINT8
## 640 x 480 image from 920k to 180k bytes, which is good, but still to much to send in one
## UDP packet. Might still make sense to compress and transfer in chuncks (with a header indicating
## number of bytes to send). Not sure how long compression takes, but likely it's faster than 
## the extra network transmission without compression.

"""
Server pseudo-code

Initialize server
Initialize screen

Start loop:
    Generate image
    Send image
    Receive inputs
    Display inputs on screen
"""

# pylint: disable=E1101
import numpy as np
import sys, pygame, time
import socket
import struct

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <host> <port>")
    sys.exit(1)
host = sys.argv[1]
port = int(sys.argv[2])
server_addr = (host, port)

pygame.init()  

# Set parameters and constants
size = width, height = 960, 480
imsize = imwidth, imheight = 640, 480
FPS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class TextPrint:
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 20)

    def print(self, screen, textString):
        textBitmap = self.font.render(textString, True, BLACK)
        screen.blit(textBitmap, [self.x, self.y])
        self.y += self.line_height
        
    def reset(self):
        self.x = imwidth + 10
        self.y = 10
        self.line_height = 15
        
    def indent(self):
        self.x += 10
        
    def unindent(self):
        self.x -= 10


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(server_addr)

print("Waiting for client connection...")

msg, addr = sock.recvfrom(4)

if msg != b'hiya':
    raise Exception("Something went wrong!")

print(f"Connected with {addr[0]}:{addr[1]}")

# Initialize stuff
screen = pygame.display.set_mode(size)
pygame.display.set_caption("RPiCar Server")

# random_image = np.zeros((imwidth, imheight, 3), dtype='uint8')
# camera_image = pygame.surfarray.make_surface(random_image).convert()

text_print = TextPrint()

# NOTE: Max size for UDP is practially around 500 bytes I guess?
counter = 0
check_sequence = [WHITE[0], BLACK[0]]

while True:
    t0 = time.time()

    # Event loop    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  
            sys.exit()

    # Reset the screen and text processor
    screen.fill(WHITE)
    text_print.reset()

    # Receive two float32s from the client, one per axis of control (throttle and steering)
    msg, addr = sock.recvfrom(8)
    if not msg:
        break
    ax1 = struct.unpack('>f', msg[:4])[0]
    ax2 = struct.unpack('>f', msg[4:])[0]

    # print("Received {:} {:} from client".format(ax1, ax2))

    text_print.print(screen, 'Inputs received from client:')
    text_print.indent()
    text_print.print(screen, 'Ax1: {:.2f}'.format(ax1))
    text_print.print(screen, 'Ax2: {:.2f}'.format(ax2))

    text_print.unindent()
    text_print.print(screen, '')
    text_print.print(screen, '<-- Image transmitted to client')

    # Get the image to transmit
    # random_image = np.zeros((imwidth, imheight, 3), dtype='uint8')
    # check_color_ndx = 0
    # for w in range(16):
    #     for h in range(12):
    #         random_image[40*w:40*(w+1), 40*h:40*(h+1), :] = check_sequence[check_color_ndx]
    #         check_color_ndx = 1 - check_color_ndx
    #     check_color_ndx = 1 - check_color_ndx

    # pygame.surfarray.blit_array(camera_image, random_image)
    # screen.blit(camera_image, (0, 0))
    
    # # random_image = random_image.tobytes()

    # counter += 1
    # if counter >= FPS:
    #     counter = 0
    #     check_sequence = [check_sequence[1], check_sequence[0]]
    
    

    # This image, as int32, is 3686400 bytes
    # That's 4096 chunks of 900 bytes
    # I'll append a sequence number so we can stitch back together on the client in order

    # print("Transmitting image...")
    # for i in range(3600):
    #     part = struct.pack('>H', i) + random_image[(i * 256):((i + 1) * 256)]
    #     sock.sendto(part, addr)
    # print("Image transmitted!")
    # Cap the FPS
    elapsed_time = time.time() - t0

    text_print.print(screen, '')
    text_print.print(screen, "Frame time: {:.2f} ms".format((elapsed_time * 1000)))

    pygame.display.flip()

    elapsed_time = time.time() - t0

    if ((1 / FPS) - elapsed_time) > 0:
        # if np.random.rand() < 0.01:
        #     print(1/elapsed_time)
        time.sleep((1 / FPS) - elapsed_time)
