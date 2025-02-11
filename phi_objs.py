import typing, math, os, random

from const import *
from func import *
from enums import *
from dxsound import *
from objs import *
from note_judge import *

LINE_LENGTH = 5.76*WINDOW_HEIGHT
LINE_WIDTH = 0.0075*WINDOW_HEIGHT

Y = 0.6*WINDOW_HEIGHT
X = 0.05625*WINDOW_WIDTH

NOTE_SOUNDS = (
    directSound.open(".\\resources\\sounds\\tap.wav"),
    directSound.open(".\\resources\\sounds\\drag.wav"),
    directSound.open(".\\resources\\sounds\\tap.wav"),
    directSound.open(".\\resources\\sounds\\flick.wav"),
)

NOTE_TEXTURES = (
    Texture.from_path(".\\resources\\textures\\Tap.png"),
    Texture.from_path(".\\resources\\textures\\Drag.png"),
    Texture.from_path(".\\resources\\textures\\Hold_Head.png"),
    Texture.from_path(".\\resources\\textures\\Flick.png"),
    Texture.from_path(".\\resources\\textures\\Hold.png").set_height(1),
    Texture.from_path(".\\resources\\textures\\Hold_End.png"),
    Texture.from_path(".\\resources\\textures\\TapHL.png"),
    Texture.from_path(".\\resources\\textures\\DragHL.png"),
    Texture.from_path(".\\resources\\textures\\Hold_HeadHL.png"),
    Texture.from_path(".\\resources\\textures\\FlickHL.png"),
    Texture.from_path(".\\resources\\textures\\Hold_Body_HL.png").set_height(1),
    Texture.from_path(".\\resources\\textures\\Hold_End_HL.png"),
)

PARTICLE_TEXTURE = [Texture.from_path(os.path.join(".\\resources\\textures\\particles", name)) for name in sorted(os.listdir(".\\resources\\textures\\particles"), key=lambda x: int(x.split(".")[0])) if name.endswith(".png")]

MAX_RENDER_FP = 2*WINDOW_HEIGHT

CUBE_SIZE = 20*WIDTH_SCALE

NOTE_SCALE = 0.1*WIDTH_SCALE

MAX_DISTANCE = 200*WIDTH_SCALE

MIN_DISTANCE = 100*WIDTH_SCALE

PARTICLE_SIZE = 0.65*WIDTH_SCALE

PARTICLE_MOVE_EASING = lambda x: 1-(1-x)**4

CUBE_DISAPPEAR_EASING = lambda x: x*x

def _phi_time_to_second(time: float, bpm: float):
    return time * (1.875 / bpm)

def _init_events(events: list[dict], bpm: float):
    events.sort(key=lambda x: x["startTime"])
    for event in events:
        event["startTime"] = _phi_time_to_second(event["startTime"], bpm)
        event["endTime"] = _phi_time_to_second(event["endTime"], bpm)

def _init_normal_events(events: list[dict], bpm: float):
    events[0]["startTime"] = -999999
    events[-1]["endTime"] = 10000000
    _init_events(events, bpm)

def _init_move_events(events: list[dict], bpm: float):
    _init_normal_events(events, bpm)
    for event in events:
        event["start"] = event["start"] * WINDOW_WIDTH
        event["end"] = event["end"] * WINDOW_WIDTH
        event["start2"] = event["start2"] * WINDOW_HEIGHT
        event["end2"] = event["end2"] * WINDOW_HEIGHT

def _init_speed_events(events: list[dict], bpm: float):
    _init_events(events, bpm)
    for event in events[:]:
        if event["endTime"] < 0:
            events.pop(0)
        else:
            events[0]["startTime"] = 0
            break
    events[-1]["endTime"] = 10000000
    fp = 0
    for event in events:
        event["fp"] = fp
        fp += (event["endTime"] - event["startTime"]) * event["value"] * Y

def get_fp(events: list[dict], time: float) -> float:
    event = _find_event(events, time)
    return event["fp"] + (time - event["startTime"]) * event["value"] * Y

def _linear(st, et, t, sv, ev): return sv+(ev-sv)*(t-st)/(et-st)

def _find_event(events: list[dict], time: float) -> typing.Optional[dict]:
    l, r = 0, len(events)-1
    while l <= r:
        m = (l + r) // 2
        e = events[m]
        st, et = e["startTime"], e["endTime"]
        if st <= time <= et: return e
        elif st > time: r = m - 1
        else: l = m + 1
    return None

def _get_event_value(events: list[dict], time: float) -> float:
    event = _find_event(events, time)
    return _linear(event["startTime"], event["endTime"], time, event["start"], event["end"])

def _get_move_event_value(events: list[dict], time: float) -> float:
    event = _find_event(events, time)
    return (
        _linear(event["startTime"], event["endTime"], time, event["start"], event["end"]),
        _linear(event["startTime"], event["endTime"], time, event["start2"], event["end2"])
        )

def rotate(x, y, r, distance):
    r = math.radians(r)
    return x+distance*math.cos(r), y+distance*math.sin(r)

def _init_notes(above, bpm, speed_events, note_datas: list[dict], function: typing.Callable[[typing.Any], bool]):
    return [Note(d, above, bpm, speed_events) for d in sorted(filter(function, note_datas), key=lambda x: x["time"])]

class judgeLine:
    def __init__(self, data: dict):
        self.bpm = data["bpm"]
        self.PARTICLE_RATE = 30 / self.bpm
        self.move_events = data["judgeLineMoveEvents"]
        self.rotate_events = data["judgeLineRotateEvents"]
        self.alpha_events = data["judgeLineDisappearEvents"]
        self.speed_events = data["speedEvents"]
        _init_move_events(self.move_events, self.bpm)
        _init_normal_events(self.rotate_events, self.bpm)
        _init_normal_events(self.alpha_events, self.bpm)
        _init_speed_events(self.speed_events, self.bpm)
        self.x, self.y = _get_move_event_value(self.move_events, 0)
        self.r = _get_event_value(self.rotate_events, 0)
        self.a = _get_event_value(self.alpha_events, 0)
        self.notes_above = _init_notes(True, self.bpm, self.speed_events, data["notesAbove"], lambda x: x["type"] != 3)
        self.notes_below = _init_notes(False, self.bpm, self.speed_events, data["notesBelow"], lambda x: x["type"] != 3)
        self.holds_above = _init_notes(True, self.bpm, self.speed_events, data["notesAbove"], lambda x: x["type"] == 3)
        self.holds_below = _init_notes(False, self.bpm, self.speed_events, data["notesBelow"], lambda x: x["type"] == 3)
        self.fp = 0
        self.particles = []
    
    def update(self, time):
        self.x, self.y = _get_move_event_value(self.move_events, time)
        self.r = _get_event_value(self.rotate_events, time)
        self.a = _get_event_value(self.alpha_events, time)
        if self.notes_above or self.notes_below or self.holds_above or self.holds_below:
            self.fp = get_fp(self.speed_events, time)
    
    def update_notes(self, time):
        self._update_notes(time)
        self._update_holds(time)
    
    def draw_particles(self, time):
        for particle in self.particles[:]:
            particle.draw(time)
            if particle.over:
                self.particles.remove(particle)
        
    def _update_notes(self, time):
        for note in self.notes_above[:]:
            note.update(self.x, self.y, self.r, self.fp, time)
            assert note.type != 2
            if note.status == NoteStatus.Judged:
                if note.judgement not in [Judgement.MISS, Judgement.BAD]:
                    color = PERFECT_COLOR if note.judgement == Judgement.PERFECT else GOOD_COLOR
                    self.particles.append(Particle(time, self.x, self.y, self.r, note.pos_x, color=color))
                self.notes_above.remove(note)
            if note.fp - self.fp > MAX_RENDER_FP:
                break
        
        for note in self.notes_below[:]:
            note.update(self.x, self.y, self.r, self.fp, time)
            if note.status == NoteStatus.Judged:
                if note.judgement not in [Judgement.MISS, Judgement.BAD]:
                    color = PERFECT_COLOR if note.judgement == Judgement.PERFECT else GOOD_COLOR
                    self.particles.append(Particle(time, self.x, self.y, self.r, note.pos_x, color=color))
                self.notes_below.remove(note)
            if note.fp - self.fp > MAX_RENDER_FP:
                break

    def _update_holds(self, time):
        for note in self.holds_above[:]:
            note.update(self.x, self.y, self.r, self.fp, time)
            if note.status == NoteStatus.Judging and note.judgement != Judgement.WILL_MISS:
                if note.judgement != Judgement.MISS:
                    if time - note.timer >= self.PARTICLE_RATE:
                        color = PERFECT_COLOR if note.judgement == Judgement.PERFECT else GOOD_COLOR
                        self.particles.append(Particle(time, self.x, self.y, self.r, note.pos_x, color=color))
                        # wtf bro
                        if config["shit"]:
                            note.timer -= (time - note.time) % (self.PARTICLE_RATE*0.26)
                        note.timer += self.PARTICLE_RATE
            elif note.status == NoteStatus.Judged:
                self.holds_above.remove(note)
            if note.fp - self.fp > MAX_RENDER_FP:
                break
        
        for note in self.holds_below[:]:
            note.update(self.x, self.y, self.r, self.fp, time)
            if note.status == NoteStatus.Judging and note.judgement != Judgement.WILL_MISS:
                if note.judgement != Judgement.MISS:
                    if time - note.timer >= self.PARTICLE_RATE:
                        color = PERFECT_COLOR if note.judgement == Judgement.PERFECT else GOOD_COLOR
                        self.particles.append(Particle(time, self.x, self.y, self.r, note.pos_x, color=color))
                        if config["shit"]:
                            note.timer -= (time - note.time) % (self.PARTICLE_RATE*0.26)
                        note.timer += self.PARTICLE_RATE
            elif note.status == NoteStatus.Judged:
                self.holds_below.remove(note)
            if note.fp - self.fp > MAX_RENDER_FP:
                break

    def draw_notes(self):
        for note in self.notes_above:
            if note.fp - self.fp > MAX_RENDER_FP:
                break
            note.draw(self.fp)

        for note in self.notes_below:
            if note.fp - self.fp > MAX_RENDER_FP:
                break
            note.draw(self.fp)

    def draw_holds(self):
        for note in self.holds_above:
            if note.fp - self.fp > MAX_RENDER_FP:
                break
            note.draw(self.fp)

        for note in self.holds_below:
            if note.fp - self.fp > MAX_RENDER_FP:
                break
            note.draw(self.fp)

    def draw(self):
        if self.a > 0:
            draw_line(self.x, self.y, LINE_LENGTH, LINE_WIDTH, self.r, self.a, color=(1, 1, 0.6))

class Note:
    def __init__(self, data, above, bpm, speed_events):
        self.time = _phi_time_to_second(data["time"], bpm)
        self.end_time = self.time + _phi_time_to_second(data["holdTime"], bpm)
        self.type = data["type"]-1
        self.status = NoteStatus.Dropping
        self.above = above
        self.speed = data["speed"] if self.type != 2 else 1
        self.fp = get_fp(speed_events, self.time)
        self.end_fp = self.fp + data["speed"] * (self.end_time-self.time) * Y
        self.hold_len = self.end_fp - self.fp
        self.pos_x = data["positionX"]*X
        self.cover = False
        self.offset = 6 if data["MP"] else 0
        self.timer = self.time - 30/bpm
        self.judgement = Judgement.PERFECT if not noautoplay else None
        self.judging = False
        self.x = 0
        self.y = 0
        self.r = 0
        self.a2 = 1
    
    def update(self, x, y, r, fp, time):
        if self.time-0.16 <= time and self not in can_judge_notes and noautoplay and self.judgement is None:
            can_judge_notes.append(self)
            can_judge_notes.sort(key=lambda x: x.time)
        if self.time < time and not noautoplay:
            if self.status == NoteStatus.Dropping:
                NOTE_SOUNDS[self.type].play()
                self.status = NoteStatus.Judged if self.type != 2 else NoteStatus.Judging
        if self.time < time:
            if self.status == NoteStatus.Dropping and self.type == 2:
                self.status = NoteStatus.Judging
            if self.status == NoteStatus.Judging and time >= self.end_time:
                self.status = NoteStatus.Judged
            if self.type != 0 and self.judgement == Judgement.PERFECT:
                NOTE_SOUNDS[self.type].play()
                self.status = NoteStatus.Judged
        cfp = (self.fp-fp if self.status != NoteStatus.Judging else 0) * self.speed
        self.r = r + (180 if not self.above else 0)
        self.x, self.y = rotate(*rotate(x, y, self.r+90, cfp), r, self.pos_x)
        if self.type == 2:
            self.end_x, self.end_y = rotate(self.x, self.y, self.r+90, self.end_fp-(self.fp if self.status == NoteStatus.Dropping else fp))
        self.cover = cfp < -0.01
        self._ = time-self.time

    def miss(self):
        self.a2 = 0.5

    def perfect(self):
        self.judgement = Judgement.PERFECT
        if self.type == 0:
            NOTE_SOUNDS[self.type].play()
            self.status = NoteStatus.Judged
        elif self.type == 2:
            NOTE_SOUNDS[self.type].play()
            self.judging = True
    
    def good(self):
        self.judgement = Judgement.GOOD
        if self.type == 0:
            NOTE_SOUNDS[self.type].play()
            self.status = NoteStatus.Judged
        elif self.type == 2:
            NOTE_SOUNDS[self.type].play()
            self.judging = True
    
    def bad(self):
        self.judgement = Judgement.BAD
        self.status = NoteStatus.Judged

    def draw(self, fp):
        a = 1 if self.judgement != Judgement.WILL_MISS else max(1-(self._)/0.16, 0)
        if (not self.cover or a < 1) and (self.type != 2 or self.hold_len > 0):
            if self.status == NoteStatus.Dropping:
                draw_texture(NOTE_TEXTURES[self.type+self.offset], self.x, self.y, NOTE_SCALE, NOTE_SCALE, self.r, a, anchor=[0.5, 1 if self.type == 2 else 0.5])
            if self.type == 2:
                if self.status == NoteStatus.Judging:
                    draw_texture(NOTE_TEXTURES[4+self.offset], self.x, self.y, NOTE_SCALE, self.end_fp-fp, self.r, self.a2, anchor=[0.5, 0])
                    draw_texture(NOTE_TEXTURES[5+self.offset], self.end_x, self.end_y, NOTE_SCALE, NOTE_SCALE, self.r, self.a2, anchor=[0.5, 0])
                elif self.status == NoteStatus.Dropping:
                    draw_texture(NOTE_TEXTURES[4+self.offset], self.x, self.y, NOTE_SCALE, self.end_fp-self.fp, self.r, self.a2, anchor=[0.5, 0])
                    draw_texture(NOTE_TEXTURES[5+self.offset], self.end_x, self.end_y, NOTE_SCALE, NOTE_SCALE, self.r, self.a2, anchor=[0.5, 0])
    
    def __eq__(self, other):
        return id(self) == id(other)

class Particle:
    def __init__(self, time, x, y, r, xpos, _type=0, color=PERFECT_COLOR):
        self.type = _type
        self.st = time
        self.over = False
        self.color = color
        if _type == 0:
            self.x, self.y = rotate(x, y, r, xpos)
            self.cubes = [Particle(time, self.x, self.y, r, 0, 1, color=color) for _ in range(4)]
        else:
            self.x, self.y = x, y
            self.distance = random.uniform(MIN_DISTANCE, MAX_DISTANCE)
            self.angle = random.uniform(0, 360)
    
    def draw(self, time):
        process_time = time - self.st
        z = process_time*2
        if process_time <= 0.5:
            if self.type == 0:
                index = process_time*60
                draw_texture(PARTICLE_TEXTURE[int(index)-1], self.x, self.y, PARTICLE_SIZE, PARTICLE_SIZE, 0, 1, anchor=[0.5, 0.5], color=self.color)
                for cube in self.cubes:
                    cube.draw(time)
            else:
                x, y = rotate(self.x, self.y, self.angle, self.distance*PARTICLE_MOVE_EASING(z))
                alpha = 1-z
                size = 1-CUBE_DISAPPEAR_EASING(z)*0.2 if z > 0.6 else 1
                draw_rect(x, y, CUBE_SIZE*size, CUBE_SIZE*size, 0, alpha, anchor=[0.5, 0.5], color=self.color)
        else:
            self.over = True