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

    dur_symbols = {
        4: "whole",
        2: "half",
        1.5: "quarter dot",
        1: "quarter",
        0.75: "8th dot",
        0.5: "8th",
        0.25: "16th",
    }

    def __init__(self, pitch, duration=1, volume=100):
        self.pitch = pitch
        self.duration = duration
        self.volume = volume

    def __str__(self):
        if self.duration in self.dur_symbols:
            dur_symbol = self.dur_symbols[self.duration]
        else:
            dur_symbol = "tied note"

        return "<Note {} {} {}>".format(
            gm.note_names[self.pitch], dur_symbol, self.volume
        )

    def __repr__(self):
        return self.__str__()


class Rest:
    """Represents a rest"""

    pitch = None
    duration = 1
    volume = None

    def __init__(self, duration=1):
        self.duration = duration

    def __str__(self):
        if self.duration in Note.dur_symbols:
            dur_symbol = Note.dur_symbols[self.duration]
        else:
            dur_symbol = "tied rest"

        return "<Rest {}>".format(dur_symbol)

    def __repr__(self):
        return self.__str__()


class Chord:
    """Represents a chord"""

    root = gm.C_2
    type = "M"
    inversion = 1
    duration = 4
    volume = 80

    # Define note relationships within chord for each inversion
    defs = {
        1: {
            "M": [0, 4, 7],
            "m": [0, 3, 7],
            "d": [0, 3, 6],
            "M7": [0, 4, 7, 11],
            "m7": [0, 3, 7, 11],
            "d7": [0, 3, 6],
        },
        2: {
            "M": [-8, -5, 0],
            "m": [-9, -5, 0],
            "d": [-9, -6, 0],
            "M7": [-8, -5, 0, -1],
            "m7": [-9, -5, 0, -1],
            "d7": [-9, -6, 0],
        },
        3: {
            "M": [-5, 0, 4],
            "m": [-5, 0, 3],
            "d": [-6, 0, 3],
            "M7": [-5, 0, 4, -1],
            "m7": [-5, 0, 3, -1],
            "d7": [-6, 0, 3],
        },
    }

    def __init__(self, root, chord_type="M", inversion=1, duration=4, volume=80):
        self.root = root
        self.type = chord_type
        self.inversion = inversion
        self.duration = duration
        self.volume = volume
        self.pitches = get_pitches()

    def spread(self):
        """Split chord into individual notes"""

        notes = tuple(
            Note(self.root + shift, duration=self.duration, volume=self.volume)
            for shift in self.defs[self.inversion][self.type]
        )

        enforce_range = [gm.A_2, gm.D_4]

        for note in notes:
            if note.pitch not in self.pitches:
                # TODO: find a better way to fix this. This happens because
                # depending on the key, the natural 7th will pick the wrong note
                note.pitch = note.pitch - 1
            if note.pitch < enforce_range[0]:
                note.pitch += 12
            if note.pitch > enforce_range[1]:
                note.pitch -= 12

        return notes

    def __str__(self):
        return "<Chord {}{} (i{})>".format(
            gm.note_names[self.root], self.type, self.inversion
        )

    def __repr__(self):
        return self.__str__()


def get_durations():
    """Get list of possible note durations and weights"""

    durations = [
        4,  # whole
        2,  # half
        1 + 1 / 2,  # dotted quarter
        1,  # quarter
        1 / 2 + 1 / 4,  # dotted 8th
        1 / 2,  # 8th
        1 / 4,  # 16th
    ]
    possible_weights = [
        (5, 10, 5, 50, 10, 50, 20),
        (80, 80, 10, 10, 10, 10, 10),
        (5, 5, 10, 10, 10, 80, 80),
    ]
    dur_weights = random.choice(possible_weights)

    return durations, dur_weights


def gen_duration(durations, dur_weights):
    """Generator for durations"""

    duration = random.choices(durations, weights=dur_weights)[0]

    if duration in [0.5, 0.25] and len(gen_duration.buffer) == 0:
        # If it was a 8th or 16th note, then make it be a group of 2 to 4 of them
        if random.choice([True, False]):
            gen_duration.buffer = [duration, duration, duration, duration]
        else:
            gen_duration.buffer = [duration, duration]

    if len(gen_duration.buffer) > 0:
        yield gen_duration.buffer.pop()
    else:
        yield duration


gen_duration.buffer = []


def get_pitches():
    """Get list of all pitches in the key"""

    key_template = [0, 2, 4, 5, 7, 9, 11]
    pitches = []
    for octave_note in range(0, 7 * 12 + 1, 12):
        pitches.extend([octave_note + n for n in key_template])

    return pitches


class Piece:
    """Generatable piece of music"""

    # The version of this generative engine
    version = 7

    def __init__(self):
        self.pitches = get_pitches()
        pass

    def generate(self, seed):
        """Generate the entire song (piece)"""

        print("-" * 32)
        print(f"Generating melody {seed}")
        print("-" * 32)

        instrument_1 = random.choice(gm.ALL_LEAD_LIKE_SET)
        instrument_2 = random.choice(gm.ALL_ACCOMPANIMENT_SET)
        instrument_3 = random.choice(gm.BASS_SET)
        print(f"Melody instrument {instrument_1}")
        print(f"Accompaniment instrument {instrument_2}")
        print(f"Bass instrument {instrument_3}")

        # Set up the random seed
        self.seed = seed
        random.seed(seed)

        self.beats_per_measure = random.choice([2, 3, 4, 5])
        print(f"Time signature: {self.beats_per_measure}/4")

        self.default_tempo = random.randint(90, 124)
        print(f"Tempo: {self.default_tempo}")

        self.durations, self.dur_weights = get_durations()
        self.bass_style = random.choice(["simple", "marco", "marching"])
        print(f"Bass style: {self.bass_style}")

        structure = self.generate_structure()

        midi = self.create_track(
            {"instrument": instrument_2, "track": 1, "channel": 1}, structure["chords"]
        )

        midi = self.create_track(
            {"instrument": instrument_3, "track": 2, "channel": 2},
            structure["bass"],
            midi=midi,
        )

        midi = self.create_track(
            {"instrument": instrument_1, "track": 0, "channel": 0},
            structure["melody"],
            midi=midi,
        )

        random.seed(None)

        return midi

    def generate_structure(self):
        """Plan out a structure for the song"""

        possible_sections = "abc"

        sections = {}
        for label in possible_sections:
            sections[label] = {}

            measures = random.choice([2, 3, 4, 8])
            chords = self.generate_chords(measures)
            if measures < 5:
                chords = chords + chords  # Double it up, but we'll get different melody
            sections[label]["chords"] = chords
            sections[label]["bass"] = self.generate_bass(chords)
            sections[label]["melody"] = self.generate_melody(chords)

        pattern = ["a"]  # Start with section a
        for _ in range(random.randint(2, 6)):
            pattern.append(random.choice(possible_sections))
        print("Pattern: {}".format("".join(pattern)))

        structure = {"chords": [], "bass": [], "melody": []}
        for label in pattern:
            print(f"Section {label}", sections[label]["chords"])
            structure["chords"].extend(sections[label]["chords"])
            structure["bass"].extend(sections[label]["bass"])
            structure["melody"].extend(sections[label]["melody"])

        # Ending
        chord = Chord(gm.C_2, "M", duration=self.beats_per_measure)
        structure["chords"].append(chord)
        structure["bass"].append(Note(gm.C_2 - 12, duration=1, volume=80))
        structure["melody"].append(
            Note(
                random.choice(chord.spread()).pitch,
                duration=self.beats_per_measure,
                volume=100,
            )
        )
        print("Ending", chord)

        return structure

    def generate_chords(self, measures=4):
        """Generate a chord progression"""

        root = gm.C_2

        # 0 1 2 3 4 5 6 7 8 9 10 11 12
        # C | D | E F | G | A |  B  C

        chords = [(0, "M"), (2, "m"), (4, "m"), (5, "M"), (7, "M"), (9, "m"), (11, "d")]
        chord_weights = [50, 30, 30, 50, 50, 30, 1]

        time = 0
        progression = []
        for _ in range(0, measures):
            # Pick which chord from the scale to use
            pick = random.choices(chords, weights=chord_weights)[0]
            root_shift, type_ = pick

            # Pick whether to turn into a 7th chord
            if random.choices([True, False], weights=(20, 80))[0]:
                type_ = "{}{}".format(type_, "7")

            # Pick an inversion of the chord to use
            inversion = random.choice([1, 2, 3])

            progression.append(
                Chord(
                    root + root_shift,
                    type_,
                    duration=self.beats_per_measure,
                    inversion=inversion,
                )
            )
            time = time + self.beats_per_measure

        return progression

    def generate_bass(self, chords):
        """Generate a bass line"""

        notes_data = []
        time = 0
        for chord in chords:
            pitch = chord.root - 12
            if self.bass_style == "marching":
                # quarter notes
                for _ in range(0, chord.duration):
                    notes_data.append(Note(pitch, 1, 80))
                    time = time + 1
            elif self.bass_style == "marco":
                # play one note, but then a quarter note at end of measure
                notes_data.append(Note(pitch, chord.duration - 1, 80))
                time = time + chord.duration - 1
                notes_data.append(Note(pitch, 1, 80))
                time = time + 1
            else:
                # play one note per measure
                notes_data.append(Note(pitch, chord.duration, 80))
                time = time + chord.duration

        return notes_data

    def generate_melody(self, chords):
        """Generate a melody"""

        notes_data = []
        for chord in chords:
            chord_note = random.choice(chord.spread())
            pitch = chord_note.pitch + 12  # An octave above
            motive = self.generate_motive(pitch, chord_note.duration)

            motive_duration = sum(n.duration for n in motive)
            if motive_duration > chord_note.duration:
                # Cut off last note to end at the measure
                up_to_last = sum(n.duration for n in motive[0:-1])
                motive[-1].duration = chord_note.duration - up_to_last

            notes_data.extend(motive)

        return notes_data

    def generate_motive(self, root, length=4):
        """Generate a little motive around a root note"""

        volume = 100
        interval_deltas = [0, 1, 2, 3, 4, 5]
        iv_weights = (90, 50, 50, 5, 5, 10)
        min_pitch = gm.C_2
        max_pitch = gm.C_5

        try:
            index = self.pitches.index(root)
        except ValueError:
            # Is an accidental; add it to the list of pitches?
            self.pitches.append(root)
            self.pitches.sort()
            index = self.pitches.index(root)

        pitch = root
        notes_data = []
        time = 0
        max_time = time + length
        while time < max_time:
            # A rest or a note?
            if random.choices([True, False], weights=(100, 40))[0]:
                note_type = "note"
            else:
                note_type = "rest"

            if note_type == "note":
                # Choose a new pitch
                interval = random.choices(interval_deltas, weights=iv_weights)[0]
                if random.choice([True, False]):
                    pitch = self.pitches[index + interval]
                    if pitch > max_pitch:
                        pitch = pitch - 12
                else:
                    pitch = self.pitches[index - interval]
                    if pitch < min_pitch:
                        pitch = pitch + 12

            # Choose a duration
            duration = next(gen_duration(self.durations, self.dur_weights))

            # Add to list of notes
            if note_type == "note":
                notes_data.append(Note(pitch, duration, volume))
            else:
                notes_data.append(Rest(duration))
            time = time + duration

        return notes_data

    def create_track(self, meta_data, notes_data, midi=None):

        if midi is None:
            track_count = 4
            midi = MIDIFile(track_count)

        track = meta_data.get("track", 0)
        channel = meta_data.get("channel", 0)
        name = meta_data.get("name", "Melody")
        tempo = meta_data.get("tempo", self.default_tempo)
        instrument = meta_data.get("instrument", 4)

        time = 0

        midi.addTempo(track, time, tempo)
        midi.addTrackName(track, time, name)
        midi.addProgramChange(track, channel, time, instrument)
        midi.addTimeSignature(
            track,
            time,
            numerator=self.beats_per_measure,
            denominator=2,  # A '2' here means quarter note (4)
            clocks_per_tick=24,
        )

        def add_note(onset_time, note):
            midi.addNote(
                track,
                channel,
                note.pitch,
                onset_time,
                note.duration - random.choice([0, 0.01, 0.02]),
                note.volume,
            )

        onset_time = 0
        for item in notes_data:
            if isinstance(item, Rest):
                # Do nothing, just go to the next time
                pass
            elif isinstance(item, Note):
                add_note(onset_time, item)
            elif isinstance(item, Chord):
                notes = item.spread()
                for note in notes:
                    add_note(onset_time, note)

            # Calculate when the next note/rest should start
            onset_time = onset_time + item.duration

        return midi


def main():

    sys.argv.pop(0)
    if len(sys.argv) > 0:
        seed = sys.argv[0]
    else:
        seed = str(random.randint(0, 65535))

    piece = Piece()
    midi = piece.generate(seed)

    filename = f"song-v{Piece.version}-{seed}.mid"

    with open(filename, "wb") as output_file:
        midi.writeFile(output_file)

    print("Playing generated piece")
    play_music(filename)
    print("done.")


if __name__ == "__main__":
    main()
