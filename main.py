import err_hook as _

import pygame

from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image
from pygame.locals import OPENGL, DOUBLEBUF

from const import *
from func import *
from parse_chart import *
from objs import *

pygame.init()
pygame.font.init()
window = pygame.display.set_mode(WINDOW_SIZE, OPENGL | DOUBLEBUF)
gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)

glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

texture = Texture.from_path(".\\resources\\textures\\TapHL.png")
font = pygame.font.Font(".\\resources\\fonts\\cmdysj.ttf", 23)
text = Text("Just for test", font)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    glClear(GL_COLOR_BUFFER_BIT)
    
    draw_texture(texture, 300, 300, .1, .1, 45, anchor=(0.5, 0.5), color=(1, 0, 0, 1))
    draw_texture(texture, 300, 300, .1, .1, 30, anchor=(0., 0.))

    pygame.display.flip()