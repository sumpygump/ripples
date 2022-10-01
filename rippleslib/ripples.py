#!/usr/bin/env python3
"""Ripples engine"""

import sys
import random

from midiutil import MIDIFile
from rich import print

from play import play_music
import gm


class Note:
    """Represents a midi note"""

    # MIDI note number
    pitch = 48

    # Number of 'beats'
    duration = 1

    # How loud it is; 0-127 per MIDI spec
    volume = 100

    dur_symbols = {4: "whole", 2: "half", 1: "quarter", 0.5: "8th", 0.25: "16th"}

    def __init__(self, pitch, duration=1, volume=100):
        self.pitch = pitch
        self.duration = duration
        self.volume = volume

    def __str__(self):
        return "<Note {} {} {}>".format(
            gm.note_names[self.pitch], self.dur_symbols[self.duration], self.volume
        )

    def __repr__(self):
        return self.__str__()


class Chord:
    """Represents a chord"""

    root = 48
    type = "M"
    inversion = 1
    duration = 4
    volume = 80

    defs = {
        "M": [0, 4, 7],
        "m": [0, 3, 7],
        "d": [0, 3, 6],
    }

    def __init__(self, root, chord_type="M", inversion=1, duration=4, volume=80):
        self.root = root
        self.type = chord_type
        self.inversion = inversion
        self.duration = duration
        self.volume = volume

    def spread(self):
        """Split chord into individual notes"""

        return (
            Note(self.root + shift, duration=self.duration, volume=self.volume)
            for shift in self.defs[self.type]
        )

    def __str__(self):
        return "<Chord {}{}>".format(gm.note_names[self.root], self.type)

    def __repr__(self):
        return self.__str__()


def generate_piece(seed):

    print("-" * 32)
    print(f"Generating melody {seed}")
    print("-" * 32)

    instrument_1 = random.choice(gm.PIANO_SET)
    instrument_2 = random.choice(gm.PAD_SET)
    print(f"Melody instrument {instrument_1}")
    print(f"Accompaniment instrument {instrument_2}")

    random.seed(seed)

    notes = generate_melody()
    print(notes)
    midi = create_track({"instrument": instrument_1, "track": 0, "channel": 0}, notes)

    chords = generate_chords()
    print(chords)
    midi = create_track(
        {"instrument": instrument_2, "track": 1, "channel": 1}, chords, midi=midi
    )

    # notes = generate_melody()
    # midi = create_track(
    # {"instrument": gm.MELODIC_TOM, "track": 1, "channel": 1}, notes, midi=midi
    # )

    random.seed(None)

    return midi


def generate_chords():
    """Generate a chord progression"""

    root = 48

    # 0 1 2 3 4 5 6 7 8 9 10 11 12
    # C | D | E F | G | A  |  B  C

    chords = [(0, "M"), (2, "m"), (4, "m"), (5, "M"), (7, "M"), (9, "m"), (11, "d")]

    time = 0
    progression = []
    for _ in range(0, 4):
        pick = random.choice(chords)
        progression.append((time, Chord(root + pick[0], pick[1])))
        time = time + 4

    return progression


def generate_melody():
    """Generate a notes_data"""

    duration = 1  # In beats
    volume = 100  # 0-127, as per the MIDI standard

    durations = [
        4,  # whole
        2,  # half
        1,  # quarter
        1 / 2,  # eighth
        1 / 4,  # sixteenth
    ]
    dur_weights = (5, 10, 50, 50, 20)

    key_template = [0, 2, 4, 5, 7, 9, 11]
    pitches = []
    for octave in range(0, 7 * 12 + 1, 12):
        pitches.extend([octave + n for n in key_template])
    interval_deltas = [0, 1, 2, 3, 4, 5, 6, 7]
    iv_weights = (90, 50, 50, 5, 5, 5, 5, 10)

    notes_data = []

    # Starting pitch
    index = random.randint(pitches.index(gm.C_3), pitches.index(gm.C_4))
    pitch = pitches[index]
    min_pitch = gm.C_2
    max_pitch = gm.C_5

    time = 0
    while time <= 17:
        interval = random.choices(interval_deltas, weights=iv_weights)[0]
        if random.choice([True, False]):
            pitch = pitches[index + interval]
            if pitch > max_pitch:
                pitch = pitch - 12
        else:
            pitch = pitches[index - interval]
            if pitch < min_pitch:
                pitch = pitch + 12

        duration = random.choices(durations, weights=dur_weights)[0]

        notes_data.append((time, Note(pitch, duration, volume)))
        time = time + duration

    return notes_data


def create_track(meta_data, notes_data, midi=None):

    if midi is None:
        track_count = 4
        midi = MIDIFile(track_count)

    track = meta_data.get("track", 0)
    channel = meta_data.get("channel", 0)
    name = meta_data.get("name", "Melody")
    tempo = meta_data.get("tempo", 120)  # In BPM
    instrument = meta_data.get("instrument", 4)

    time = 0

    midi.addTempo(track, time, tempo)
    midi.addTrackName(track, time, name)
    midi.addProgramChange(track, channel, time, instrument)

    def add_note(start_time, note):
        midi.addNote(
            track,
            channel,
            note.pitch,
            start_time,
            note.duration - random.choice([0, 0.1, 0.2]),
            note.volume,
        )

    for note_time, item in notes_data:
        if isinstance(item, Note):
            add_note(note_time, item)
        elif isinstance(item, Chord):
            notes = item.spread()
            for note in notes:
                add_note(note_time, note)

    return midi


def main():

    sys.argv.pop(0)
    if len(sys.argv) > 0:
        seed = sys.argv[0]
    else:
        seed = str(random.randint(0, 65535))

    midi = generate_piece(seed)

    filename = "piece-00.mid"

    with open(filename, "wb") as output_file:
        midi.writeFile(output_file)

    print("Playing generated piece")
    play_music(filename)
    print("thanks")


if __name__ == "__main__":
    main()
