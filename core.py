import phi_objs

from parse_chart import *
from dxsmixer import *
from PIL import Image, ImageFilter, ImageEnhance
from const import *
from func import *
from objs import *

def _init_background(img: Image.Image):
    if img.width < img.height:
        img = img.resize(to_int(WINDOW_WIDTH, img.height * WINDOW_WIDTH / img.width))
        img = img.crop(to_int(0, img.height/2-WINDOW_HEIGHT/2, WINDOW_WIDTH, img.height/2+WINDOW_HEIGHT/2))
    else:
        img = img.resize(to_int(img.width * WINDOW_HEIGHT / img.height, WINDOW_HEIGHT))
        img = img.crop(to_int(img.width/2-WINDOW_WIDTH/2, 0, img.width/2+WINDOW_WIDTH/2, WINDOW_HEIGHT))
    filter = ImageFilter.GaussianBlur(75)
    img = img.filter(filter)
    enhance = ImageEnhance.Brightness(img)
    img = enhance.enhance(0.4)
    return img

def phi_init(chart: Chart):
    lines = [phi_objs.judgeLine(data) for data in chart.chart["judgeLineList"]]
    music = musicCls()
    music.load(chart.music)
    bg = chart.bg
    bg = _init_background(bg)
    return lines, music, Texture.from_image(bg)

def phi_update(lines: phi_objs.judgeLine, time):
    for line in lines:
        line.update(time)
        line.update_notes(time)
def phi_draw(lines: phi_objs.judgeLine, bg):
    draw_texture(bg, 0, 0, 1, 1, 0, 1)
    for line in lines:
        line.draw()
    for line in lines:
        line.draw_holds()
    for line in lines:
        line.draw_notes()