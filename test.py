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


# pylint: disable=E1101
import numpy as np
import sys, pygame, time

pygame.init()  

# Set parameters and constants
size = width, height = 960, 480
imsize = imwidth, imheight = 640, 480
FPS = 30
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


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
pygame.display.set_caption("RPiCar")

random_image = (np.random.rand(imwidth, imheight, 3) * 255).astype(int)
camera_image = pygame.surfarray.make_surface(random_image).convert()

text_print = TextPrint()
pygame.joystick.init()

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

    # Get the image to display and draw
    random_image = np.zeros((imwidth, imheight, 3), dtype='int32')
    check_color_ndx = 0
    for w in range(16):
        for h in range(12):
            random_image[40*w:40*(w+1), 40*h:40*(h+1), :] = check_sequence[check_color_ndx]
            check_color_ndx = 1 - check_color_ndx
        check_color_ndx = 1 - check_color_ndx

    counter += 1
    if counter >= FPS:
        counter = 0
        check_sequence = [check_sequence[1], check_sequence[0]]

    pygame.surfarray.blit_array(camera_image, random_image)
    screen.blit(camera_image, (0, 0))

    # Handle joystick inputs
    if pygame.joystick.get_count() == 0:
        raise Exception('No controller found!')

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    name = joystick.get_name().replace('Controller', '').replace('(', '').replace(')', '')
    if "xbox one" not in name.lower():
        raise Exception("Only XBox One controllers are supported")
    text_print.print(screen, "Joystick name: {}".format(name))

    # Usually axis run in pairs, up/down for one, and left/right for
    # the other.
    axes = joystick.get_numaxes()
    text_print.print(screen, "Number of axes: {}".format(axes))
    text_print.indent()
    
    for i in range(axes):
        axis = joystick.get_axis(i)
        text_print.print(screen, "Axis {} value: {:>6.3f}".format(i, axis))
    text_print.unindent()
        
    buttons = joystick.get_numbuttons()
    text_print.print(screen, "Number of buttons: {}".format(buttons))
    text_print.indent()

    for i in range(buttons):
        button = joystick.get_button(i)
        text_print.print(screen, "Button {:>2} value: {}".format(i, button))
    text_print.unindent()
        
    # Hat switch. All or nothing for direction, not like joysticks.
    # Value comes back in an array.
    hats = joystick.get_numhats()
    text_print.print(screen, "Number of hats: {}".format(hats))
    text_print.indent()

    for i in range(hats):
        hat = joystick.get_hat(i)
        text_print.print(screen, "Hat {} value: {}".format(i, str(hat)))
    text_print.unindent()

    pygame.display.flip()

    # Cap the FPS
    elapsed_time = time.time() - t0

    if ((1 / FPS) - elapsed_time) > 0:
        # if np.random.rand() < 0.01:
        #     print(1/elapsed_time)
        time.sleep((1 / FPS) - elapsed_time)
