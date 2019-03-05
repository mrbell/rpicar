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


"""
Client pseudo-code

Initialize socket
Initialize screen

Write wake up connection to server

Start loop:
    Get inputs
    Send inputs
    Read image
    Display inputs and image on screen
"""

# pylint: disable=E1101
import numpy as np
import sys, pygame, time
import socket
import struct

if len(sys.argv) != 4:
    print(f"Usage: {sys.argv[0]} <host> <port> <myport>")
    sys.exit(1)
host = sys.argv[1]
port = int(sys.argv[2])
myport = int(sys.argv[3])
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


# Initialize stuff
screen = pygame.display.set_mode(size)
pygame.display.set_caption("RPiCar Client")

random_image = np.zeros((imwidth, imheight, 3), dtype='int32')
camera_image = pygame.surfarray.make_surface(random_image).convert()

text_print = TextPrint()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', myport))
sock.sendto(b'hiya', server_addr)

while True:
    t0 = time.time()

    # Event loop    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  
            sys.exit()

    # Reset the screen and text processor
    screen.fill(WHITE)
    text_print.reset()

    text_print.print(screen, '<-- Image received from server')

    # Get the image to transmit
    image_parts = []
    for i in range(3600):
        part, addr = sock.recvfrom(258)
        if not part:
            raise Exception('connection to server lost')
        image_parts.append((
            struct.unpack('>H', part[:2]),
            part[2:]
        ))
    sock.sendto(b'g2g!', server_addr)
    image_parts = sorted(image_parts, key=lambda x: x[0])

    random_image = b''
    for part in image_parts:
        random_image += part[1]
    random_image = np.frombuffer(random_image, dtype='uint8').reshape((imwidth, imheight, 3))

    pygame.surfarray.blit_array(camera_image, random_image)
    screen.blit(camera_image, (0, 0))

    # Cap the FPS
    elapsed_time = time.time() - t0

    text_print.print(screen, '')
    text_print.print(screen, "Frame time: {:.2f} ms".format((elapsed_time * 1000)))

    pygame.display.flip()

    elapsed_time = time.time() - t0

    if ((1 / FPS) - elapsed_time) > 0:
        time.sleep((1 / FPS) - elapsed_time)
