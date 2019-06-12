import logging
import sys
import numpy as np
import pygame
from pygame.locals import *

from helpers import *

LOGGER = logging.getLogger(__name__)

# constants
INF = float('inf')
GOAL_RADIUS = 10


############################################################


def check_pygame_enabled(func):
    """Pythonic decorator that force function to do Nothing
    if pygame is not enabled"""

    def wrapper(*args, **kwargs):
        if not args[0].enable_pygame:
            return
        return func(*args, **kwargs)

    return wrapper


class MAPD:
    def __init__(self, args):
        self.args = args
        # initialize and prepare screen
        self.block_size = int(args['--block-size'])
        self.output_file = str(args['<OUTPUT_FILE>'])
        self.SCALING = float(args['--scaling'])
        # self.img = pygame.image.load(image)

        self.extra = 0

        self.pygame_init()

        self.map = np.ones((self.XDIM // self.block_size + 1,
                            self.YDIM // self.block_size + 1
                            ), dtype=int)

        self.update_screen(update_all=True)
        print('map size is:', self.map.shape)

    ############################################################

    def pygame_init(self, enable_pygame=True):
        self.enable_pygame = enable_pygame
        pygame.init()
        self.fpsClock = pygame.time.Clock()
        # self.fpsClock.tick(10)
        self.fpsClock.tick(1)
        pygame.display.set_caption('MAPD')
        # screen.fill(white)
        ################################################################################
        # text
        pygame.font.init()
        self.img = pygame.image.load('intel_lab.png')
        self.XDIM = self.img.get_width()
        self.YDIM = self.img.get_height()
        self.myfont = pygame.font.SysFont('Arial',
                                          int(self.XDIM * 0.04 * self.SCALING))
        ################################################################################
        # main window

        self.window = pygame.display.set_mode([
            int(self.XDIM * self.SCALING),
            int((self.YDIM + self.extra) * self.SCALING)
        ])
        self.aaaa = 0

        self.grid_lines = pygame.Surface(
            (self.XDIM * self.SCALING, self.YDIM * self.SCALING),
            pygame.SRCALPHA)
        self.grid_block = pygame.Surface(
            (self.block_size * self.SCALING, self.block_size * self.SCALING),
            pygame.SRCALPHA)

        ################################################################################
        # background aka the room
        ################################################################################

        self.background = pygame.Surface([self.XDIM, (self.YDIM + self.extra)])
        self.background.blit(self.img, (0, 0))
        # resize background to match windows
        self.background = pygame.transform.scale(self.background, [
            int(self.XDIM * self.SCALING),
            int((self.YDIM + self.extra) * self.SCALING)
        ])

        self.agents_layer = pygame.Surface(
            (self.XDIM * self.SCALING, self.YDIM * self.SCALING),
            pygame.SRCALPHA)
        ################################################################################
        ################################################################################
        if not self.enable_pygame:
            self.pygame_hide()

    def pygame_show(self):
        self.enable_pygame = True

    def pygame_hide(self):
        self.enable_pygame = False
        pygame.display.iconify()
        # pygame.quit()

    ############################################################
    ##                    TEST FUNCS                      ##
    ############################################################

    def run(self):
        """Run until the end of the world"""

        class ReturnKeyPressedAlert(Exception):
            """To tell outer block enter key has been pressed."""
            pass

        # spawn all desire agents
        self.show_banner_text('click on area to create blocks')
        pygame.display.update()
        mouse_pressed = False
        add_block_mode = None
        while True:

            try:
                for e in pygame.event.get():
                    if e.type == MOUSEMOTION:
                        mousePos = [int(e.pos[0] / self.SCALING),
                                    int(e.pos[1] / self.SCALING)]

                        mousePos[0] = mousePos[0] // self.block_size
                        mousePos[1] = mousePos[1] // self.block_size
                        mousePos = tuple(mousePos)

                    elif e.type == MOUSEBUTTONDOWN:
                        mouse_pressed = True
                        if self.map[mousePos] == 1:
                            add_block_mode = False
                        else:
                            add_block_mode = True


                    elif e.type == MOUSEBUTTONUP:
                        mouse_pressed = False

                    elif (e.type == KEYUP and e.key == K_RETURN):
                        # hacky way to notify outer block to finish spawning agents
                        raise ReturnKeyPressedAlert()

                if mouse_pressed:

                    # print(mousePos)
                    if add_block_mode:
                        self.map[mousePos] = 1
                    else:
                        self.map[mousePos] = 0

                self.update_screen()

            except ReturnKeyPressedAlert:
                # remove any agent without task
                import pprint, os
                # transpose to flip x/y axis
                output_map = self.map.T

                newline_token = ' ;\n'
                np.savetxt(self.output_file, output_map.astype(int), delimiter=' ', newline=newline_token, fmt='%i')

                # workaround to quickly remove the last ';\n' from file.
                with open(self.output_file, 'rb+') as filehandle:
                    filehandle.seek(-len(newline_token), os.SEEK_END)
                    filehandle.truncate()
                print()
                with open(self.output_file, 'r') as f:
                    sys.stdout.write(''.join(f.readlines()))
                    sys.stdout.flush()
                print()
                print()
                print('Mpa saved as "{}"'.format(self.output_file))

    ############################################################
    ##                    DRAWING RELATED                     ##
    ############################################################

    @check_pygame_enabled
    def update_screen(self, count=0, update_all=False):
        self.window.blit(self.background, (0, 0))

        def change_block_colour(colour):
            self.grid_block.fill(colour)

        def block_text(coordinate, character):
            text = self.myfont.render(character, True, Colour.white)
            text_rect = text.get_rect(center=coordinate)
            self.window.blit(text, text_rect)

        self.grid_lines.fill(pygame.SRCALPHA)
        # paint obsticles
        for i in range(self.map.shape[0]):
            for j in range(self.map.shape[1]):
                if self.map[(i, j)] == 1:
                    change_block_colour(pygame.SRCALPHA)
                else:
                    change_block_colour((0, 255, 0, 125))
                self.window.blit(
                    self.grid_block,
                    (i * self.block_size * self.SCALING,
                     j * self.block_size * self.SCALING))

        # draw grid lines
        for i in range(max(self.map.shape[0], self.map.shape[1])):
            z = i * self.block_size * self.SCALING
            pygame.draw.line(self.grid_lines, (0, 0, 0),
                             (z, 0), (z, self.YDIM * self.SCALING),
                             1  # line width
                             )
            pygame.draw.line(self.grid_lines, (0, 0, 0),
                             (0, z),
                             (self.XDIM * self.SCALING, z),
                             1  # line width
                             )

        self.window.blit(self.grid_lines, (0, 0))
        pygame.display.update()

    def show_banner_text(self, text):
        self.window.blit(
            self.myfont.render(text, False, Colour.white, Colour.black),
            (10, (self.YDIM + self.extra) * self.SCALING * 0.95))
