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
    lines, music, bg, ui, note_score, offset = phi_init(chart)

key_pressed = {}

offset += int(get_value("offset", "0"))/1000

music.play()

length = music.get_length()
clock = pygame.time.Clock()
while True:
    events = []
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            key_pressed[event.key] = True
            events.append(event.key)
        if event.type == pygame.KEYUP:
            key_pressed.pop(event.key)
    glClear(GL_COLOR_BUFFER_BIT)

    clock.tick()

    now_time = music.get_pos()+offset

    if chart.format[0] == "Phi":
        phi_update(lines, now_time, events, key_pressed, ui)
        phi_draw(lines, bg, now_time, ui, now_time/length)

    pygame.display.flip()