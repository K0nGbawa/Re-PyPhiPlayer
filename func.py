import math, sys

from PIL import Image

from const import *
from objs import *

def get_length(pos1: tuple[float, float], pos2: tuple[float, float]) -> float:
    w = pos2[0]-pos1[0]
    h = pos2[1]-pos1[1]
    return math.sqrt(w**2+h**2)
    
def draw_texture(texture: Texture, x, y, sw, sh, r, a, anchor:tuple[float] | list[float]=(0, 0), color:tuple[float] | list[float]=(1., 1., 1.)):
    w, h = texture.width*sw, texture.height*sh
    x_offset, y_offset = -anchor[0]*w, -anchor[1]*h
    glColor(*color, a)
    glPushMatrix()
    glTranslatef(x, y, 0)
    glRotate(r, 0., 0., 1.)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture.texture_id)
    glBegin(GL_QUADS)
    glTexCoord2f(0., 0.)
    glVertex2f(x_offset, y_offset)
    glTexCoord2f(1., 0.)
    glVertex2f(w+x_offset, y_offset)
    glTexCoord2f(1., 1.)
    glVertex2f(w+x_offset, h+y_offset)
    glTexCoord2f(0., 1.)
    glVertex2f(x_offset, h+y_offset)
    glEnd()
    glBindTexture(GL_TEXTURE_2D, 0)
    glDisable(GL_TEXTURE_2D)
    glPopMatrix()

def draw_rect(x, y, w, h, r, a, anchor:tuple[float] | list[float]=(0, 0), color:tuple[float] | list[float]=(1., 1., 1.)):
    x_offset, y_offset = -anchor[0]*w, -anchor[1]*h
    glColor(*color, a)
    glPushMatrix()
    glTranslatef(x, y, 0)
    glRotate(r, 0., 0., 1.)
    glBegin(GL_QUADS)
    glTexCoord2f(0., 0.)
    glVertex2f(x_offset, y_offset)
    glTexCoord2f(1., 0.)
    glVertex2f(w+x_offset, y_offset)
    glTexCoord2f(1., 1.)
    glVertex2f(w+x_offset, h+y_offset)
    glTexCoord2f(0., 1.)
    glVertex2f(x_offset, h+y_offset)
    glEnd()
    glPopMatrix()

def draw_line(x, y, length, width, r, a, color=(1, 1, 1)):
    draw_rect(x, y, length, width, r, a, anchor=[0.5, 0.5], color=color)

def to_int(*x) -> tuple[int]:
    return tuple(round(i) for i in x)


class Text:
    def __init__(self, text: str, font: pygame.font.Font):
        self.text = None
        self.font = font
        self.texture = None
        self.change_text(text)
    
    def render(self, x, y, sw, sh, r, a, anchor=(0, 0), color=(1, 1, 1)):
        if self.texture is not None:
            draw_texture(self.texture, x*WINDOW_WIDTH, y*WINDOW_HEIGHT, sw, sh, r, a, anchor, color)
    
    def change_text(self, text: str):
        if self.text != text:
            if self.texture is not None:
                glDeleteTextures(1, [self.texture.texture_id])
            text_img = self.font.render(text, True, (255, 255, 255))
            w, h = text_img.get_size()
            self.text = text
            self.texture = Texture.from_bytes_with_wh("RGBA", pygame.image.tobytes(text_img, "RGBA"), w, h)