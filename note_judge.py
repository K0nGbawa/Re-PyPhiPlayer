from dataclasses import dataclass

from enums import *
from const import *

can_judge_notes = []

@dataclass
class judges:
    perfect: int
    good: int
    bad: int
    miss: int
    combo: int

judges = judges(0,0,0,0,0)

def remove_note(x):
    if x in can_judge_notes:
        can_judge_notes.remove(x)

def update_judge_notes(events, pkeys, time):
    for note in can_judge_notes[:]:
        if pkeys and note.type not in [0, 2]:
            note.perfect()
            judges.perfect += 1
            judges.combo += 1
            remove_note(note)
        if events:
            if note.type in [0, 2] and not note.judging:
                for event in events[:]:
                    t = abs(time - note.time)
                    if t <= 0.08:
                        note.perfect()
                        events.remove(event)
                        if note.type != 2:
                            judges.perfect += 1
                            judges.combo += 1
                            remove_note(note)
                        else:
                            note.judging = True
                        break
                    elif t <= 0.16:
                        note.good()
                        events.remove(event)
                        if note.type != 2:
                            judges.good += 1
                            judges.combo += 1
                            remove_note(note)
                        else:
                            note.judging = True
                        break
                    elif t <= 0.18 and note.type == 0:
                        note.bad()
                        judges.bad += 1
                        judges.combo = 0
                        events.remove(event)
                        remove_note(note)
                        break
        if note.judging:
            if not pkeys:
                note.miss()
                judges.combo = 0
                judges.miss += 1
                remove_note(note)
            elif note.end_time-0.2 <= time:
                judges.combo += 1
                match note.judgement:
                    case Judgement.PERFECT:
                        judges.perfect += 1
                    case Judgement.GOOD:
                        judges.good += 1
                remove_note(note)
        elif note.time+0.16 < time:
            note.judgement = Judgement.MISS
            if note.type != 2:
                note.status = NoteStatus.Judged
            else:
                note.miss()
            judges.miss += 1
            judges.combo = 0
            remove_note(note)
        elif note.time < time and note.judgement is None:
            note.judgement = Judgement.WILL_MISS