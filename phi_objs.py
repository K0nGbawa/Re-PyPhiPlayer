import typing, math

from const import *
from func import *
from enums import *
from dxsound import *
from objs import *

LINE_LENGTH = 5.76*WINDOW_WIDTH
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
)

MAX_RENDER_FP = 2*WINDOW_HEIGHT

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
        self.notes_above = _init_notes(True, self.bpm, self.speed_events, data["notesAbove"], lambda x: x != 3)
        self.notes_below = _init_notes(False, self.bpm, self.speed_events, data["notesBelow"], lambda x: x != 3)
        self.holds_above = _init_notes(True, self.bpm, self.speed_events, data["notesAbove"], lambda x: x == 3)
        self.holds_below = _init_notes(False, self.bpm, self.speed_events, data["notesBelow"], lambda x: x == 3)
        self.fp = 0
    
    def update(self, time):
        self.x, self.y = _get_move_event_value(self.move_events, time)
        self.r = _get_event_value(self.rotate_events, time)
        self.a = _get_event_value(self.alpha_events, time)
        if self.notes_above or self.notes_below:
            self.fp = get_fp(self.speed_events, time)
    
    def update_notes(self, time):
        self._update_notes(time)
        self._update_holds(time)
        
    def _update_notes(self, time):
        for note in self.notes_above[:]:
            note.update(self.x, self.y, self.r, self.fp, time)
            if note.status == NoteStatus.Judged:
                self.notes_above.remove(note)
            if note.fp - self.fp > MAX_RENDER_FP:
                break
        
        for note in self.notes_below[:]:
            note.update(self.x, self.y, self.r, self.fp, time)
            if note.status == NoteStatus.Judged:
                self.notes_below.remove(note)
            if note.fp - self.fp > MAX_RENDER_FP:
                break

    def _update_holds(self, time):
        for note in self.holds_above[:]:
            note.update(self.x, self.y, self.r, self.fp, time)
            if note.status == NoteStatus.Judged:
                self.notes_above.remove(note)
            if note.fp - self.fp > MAX_RENDER_FP:
                break
        
        for note in self.holds_below[:]:
            note.update(self.x, self.y, self.r, self.fp, time)
            if note.status == NoteStatus.Judged:
                self.notes_below.remove(note)
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
        self.fp = get_fp(speed_events, self.time)
        self.end_fp = get_fp(speed_events, self.end_time) if self.type == 2 else 0
        self.speed = data["speed"]
        self.pos_x = data["positionX"]*X
        self.cover = False
        self.x = 0
        self.y = 0
        self.r = 0
    
    def update(self, x, y, r, fp, time):
        cfp = self.fp-fp if self.status != NoteStatus.Judging else 0
        if self.time < time:
            if self.status == NoteStatus.Dropping:
                NOTE_SOUNDS[self.type].play()
                self.status = NoteStatus.Judged if self.type != 2 else NoteStatus.Judging
            if self.status == NoteStatus.Judging and time >= self.end_time:
                self.status = NoteStatus.Judged
        r = r + (180 if not self.above else 0)
        self.r = r
        self.x, self.y = rotate(*rotate(x, y, r+90, cfp), r, self.pos_x)
        if self.type == 2:
            self.end_x, self.end_y = rotate(self.x, self.y, r+90, self.end_fp-(self.fp if self.status == NoteStatus.Dropping else fp))
        self.cover = cfp < -0.01
    
    def draw(self, fp):
        if not self.cover:
            if self.status == NoteStatus.Dropping:
                draw_texture(NOTE_TEXTURES[self.type], self.x, self.y, 0.1, 0.1, self.r, 1, anchor=[0.5, 1 if self.type == 3 else 0.5])
            if self.type == 2:
                if self.status == NoteStatus.Judging:
                    draw_texture(NOTE_TEXTURES[4], self.x, self.y, 0.1, self.end_fp-fp, self.r, 1, anchor=[0.5, 0])
                    draw_texture(NOTE_TEXTURES[5], self.end_x, self.end_y, 0.1, 0.1, self.r, 1, anchor=[0.5, 0])
                elif self.status == NoteStatus.Dropping:
                    draw_texture(NOTE_TEXTURES[4], self.x, self.y, 0.1, self.end_fp-self.fp, self.r, 1, anchor=[0.5, 0])
                    draw_texture(NOTE_TEXTURES[5], self.end_x, self.end_y, 0.1, 0.1, self.r, 1, anchor=[0.5, 0])