from enums import *
from const import *

can_judge_notes = []

def update_judge_notes(events, pkeys, time):
    for note in can_judge_notes[:]:
        if pkeys and note.type not in [0, 2]:
            note.perfect()
            can_judge_notes.remove(note)
        if events:
            if note.type in [0, 2] and not note.judging:
                for event in events[:]:
                    t = abs(time - note.time)
                    if t <= 0.08:
                        note.perfect()
                        events.remove(event)
                        if note.type != 2:
                            can_judge_notes.remove(note)
                        else:
                            note.judging = True
                    elif t <= 0.16:
                        note.good()
                        events.remove(event)
                        if note.type != 2:
                            can_judge_notes.remove(note)
                        else:
                            note.judging = True
                    elif t <= 0.18 and note.type == 0:
                        note.bad()
                        events.remove(event)
                        can_judge_notes.remove(note)
        if note.judging and not pkeys:
            note.miss()
            can_judge_notes.remove(note)
        elif note.judging and pkeys and note.end_time > time:
            can_judge_notes.remove(note)
        elif note.time+0.16 < time:
            note.judgement = Judgement.MISS
            if note.type != 2:
                note.status = NoteStatus.Judged
            else:
                note.miss()
            can_judge_notes.remove(note)
        elif note.time < time:
            note.judgement = Judgement.WILL_MISS