import pygame

import phi_objs

from parse_chart import *
from dxsmixer import *
from PIL import Image, ImageFilter, ImageEnhance
from const import *
from func import *
from objs import *
from note_judge import *

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
    ui = phiUI(chart.name, chart.level)
    times = {}
    notes = [phi_objs._phi_time_to_second(note["time"], line["bpm"]) for line in chart.chart["judgeLineList"] for note in line["notesAbove"]+line["notesBelow"]]
    for note in notes:
        if note not in times: times[note] = 1
        else: times[note] += 1
    for line in chart.chart["judgeLineList"]:
        for note in line["notesAbove"]:
            note["MP"] = times[phi_objs._phi_time_to_second(note["time"], line["bpm"])] > 1
        for note in line["notesBelow"]:
            note["MP"] = times[phi_objs._phi_time_to_second(note["time"], line["bpm"])] > 1
    lines = [phi_objs.judgeLine(data) for data in chart.chart["judgeLineList"]]
    music = musicCls()
    music.load(chart.music)
    bg = chart.bg
    bg = _init_background(bg)
    return lines, music, Texture.from_image(bg), ui, 1000000/len(notes)

def phi_update(lines: phi_objs.judgeLine, time, event, pkeys):
    update_judge_notes(event, pkeys, time)
    for line in lines:
        line.update(time)
        line.update_notes(time)
    
def phi_draw(lines: phi_objs.judgeLine, bg, time, ui, process):
    draw_texture(bg, 0, 0, 1, 1, 0, 1)
    for line in lines:
        line.draw()
    for line in lines:
        line.draw_holds()
    for line in lines:
        line.draw_notes()
    for line in lines:
        line.draw_particles(time)
    ui.render(process)

class phiUI:
    def __init__(self, name, level):
        font = pygame.font.Font(PGR_FONT, 30)
        combo_label_font = pygame.font.Font(PGR_FONT, 14)
        combo_num_font = pygame.font.Font(PGR_FONT, 44)
        self.score = 0
        self.combo = 0
        self.name = Text(name, font)
        self.level = Text(level, font)
        self.score_num = Text(str(round(self.score)).zfill(7), font)
        self.combo_label = Text("COMBO", combo_label_font)
        self.combo_num = Text(str(self.combo), combo_num_font)
        self.pause = Texture.from_path(".\\resources\\textures\\Pause.png")

    def render(self, process):
        draw_rect(0, WINDOW_HEIGHT, process*WINDOW_WIDTH, BAR_WIDTH, 0, 1, anchor=(0, 1), color=(0.6, 0.6, 0.6))
        draw_rect(process*WINDOW_WIDTH, WINDOW_HEIGHT, 2*WIDTH_SCALE, BAR_WIDTH, 0, 1, anchor=(1, 1), color=(1, 1, 1))
        self.name.render(0.025, 0.025, 0.85, 0.85, 0, 1)
        self.level.render(0.975, 0.025, 0.85, 0.85, 0, 1, anchor=(1, 0))
        self.score_num.render(0.975, 0.965, 1, 1, 0, 1, anchor=(1, 1))
        draw_texture(self.pause, 0.03*WINDOW_WIDTH, 0.955*WINDOW_HEIGHT, 0.12*WIDTH_SCALE, 0.12*WIDTH_SCALE, 0, 1, anchor=(0, 1))
        if self.combo >= 3:
            self.combo_label.render(0.5, 0.895, 1, 1, 0, 1, anchor=(0.5, 0.5))
            self.combo_num.render(0.5, 0.94, 1, 1, 0, 1, anchor=(0.5, 0.5))
    
    def change_combo(self, combo, note_socre):
        if self.combo != combo:
            self.combo = combo
            self.combo_num.change_text(str(self.combo))
            self.score = combo * note_socre
            self.score_num.change_text(str(round(self.score)).zfill(7))