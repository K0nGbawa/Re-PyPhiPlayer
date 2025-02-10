import err_hook as _

import pygame

from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image
from pygame.locals import OPENGL, DOUBLEBUF

from const import *

pygame.init()
pygame.font.init()
window = pygame.display.set_mode(WINDOW_SIZE, OPENGL | DOUBLEBUF)

from func import *
from parse_chart import *
from objs import *
from core import *

gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)

glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

chart = Chart(config["chart"])

if chart.format[0] == "Phi":
    lines, music, bg = phi_init(chart)

music.play()

fps = Text("", pygame.font.Font(".\\resources\\fonts\\cmdysj.ttf", 20))
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    glClear(GL_COLOR_BUFFER_BIT)

    clock.tick()

    if chart.format[0] == "Phi":
        phi_update(lines, music.get_pos())
        phi_draw(lines, bg)
    fps.change_text(f"fps:{clock.get_fps()}")
    fps.render(0, 0, 1, 1, 0, 1)

    pygame.display.flip()