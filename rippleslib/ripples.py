#!/usr/bin/env python3
"""Ripples engine"""

import sys
import random

from midiutil import MIDIFile

import gm
from play import play_music

MIN_TEMPO = 90
MAX_TEMPO = 124


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
        pitch = max(pitch, 0)
        pitch = min(pitch, 127)
        self.pitch = pitch
        self.duration = duration
        self.volume = volume

    @property
    def name(self):
        return gm.NOTE_NAMES[self.pitch]

    @property
    def note_class(self):
        return gm.NOTE_CLASS[self.pitch]

    def __str__(self):
        if self.duration in self.dur_symbols:
            dur_symbol = self.dur_symbols[self.duration]
        else:
            dur_symbol = f"tie dur:{self.duration}"

        return "<Note {} {} {}>".format(
            gm.NOTE_NAMES[self.pitch], dur_symbol, self.volume
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
            dur_symbol = f"tie dur:{self.duration}"

        return "<Rest {}>".format(dur_symbol)

    def __repr__(self):
        return self.__str__()


class Chord:
    """Represents a chord"""

    root = gm.NOTE_NUMS["C_2"]
    quality = "M"
    inversion = 1
    duration = 4
    volume = 80

    # Define note relationships within each chord quality
    defs = {
        "M": [0, 4, 7],
        "m": [0, 3, 7],
        "d": [0, 3, 6],
        "sus2": [0, 2, 7],
        "sus4": [0, 5, 7],
        "M7": [0, 4, 7, 10],
        "Mmaj7": [0, 4, 7, 11],
        "m7": [0, 3, 7, 10],
        "mmaj7": [0, 3, 7, 11],
        "d7": [0, 3, 6, 9],
        "dmin7dim5": [0, 3, 6, 10],
        "M7dim5": [0, 4, 6, 10],
        "7sus2": [0, 2, 7, 10],
        "7sus4": [0, 5, 7, 10],
    }

    def __init__(self, root, quality="M", inversion=0, duration=4, volume=80):
        self.root = root
        self.quality = quality
        self.inversion = inversion
        self.duration = duration
        self.volume = volume
        self.pitches = get_pitches()

    @property
    def name(self):
        return "{}{}".format(gm.NOTE_CLASS[self.root], self.quality)

    def spread(self, clamp=False, clamp_range=None):
        """Split chord into individual notes"""

        notes = tuple(
            Note(self.root + shift, duration=self.duration, volume=self.volume)
            for shift in self.defs[self.quality]
        )

        if clamp_range is None:
            clamp_range = [gm.NOTE_NUMS["A_1"], gm.NOTE_NUMS["D_3"]]

        if self.inversion == 1:
            notes[0].pitch += 12

        if self.inversion == 2:
            notes[0].pitch += 12
            notes[1].pitch += 12

        for note in notes:
            if clamp:
                if note.pitch < clamp_range[0]:
                    note.pitch += 12
                if note.pitch > clamp_range[1]:
                    note.pitch -= 12

        return notes

    def __str__(self):
        return "<Chord {} (i{})>".format(self.name, self.inversion)

    def __repr__(self):
        return self.__str__()


class NoteDurationStrategy:
    """Strategy (choices and weights) for probability of note durations"""

    durations = [
        4,  # whole
        2,  # half
        1 + 1 / 2,  # dotted quarter
        1,  # quarter
        1 / 2 + 1 / 4,  # dotted 8th
        1 / 2,  # 8th
        1 / 4,  # 16th
    ]
    possible_weights = {
        "balanced": (5, 10, 5, 50, 10, 50, 20),
        "long_leaning": (80, 80, 10, 10, 10, 10, 10),
        "brisk_leaning": (5, 5, 10, 10, 10, 80, 80),
    }

    @classmethod
    def select_duration_profile(cls):
        """Select the weight profile for getting a random duration value"""

        selected_profile = random.choice(list(cls.possible_weights.keys()))
        cls.duration_weights = cls.possible_weights[selected_profile]

        return selected_profile

    @classmethod
    def get_duration(cls):
        """Pick a duration using strategy profile"""

        return random.choices(
            NoteDurationStrategy.durations,
            weights=NoteDurationStrategy.duration_weights,
        )[0]


def gen_duration():
    """Generator for durations"""

    duration = NoteDurationStrategy.get_duration()

    if duration in [0.5, 0.25] and len(gen_duration.buffer) == 0:
        # If it was a 8th or 16th note, then make it be a group of 2 to 4 of them
        if random.choice([True, False]):
            gen_duration.buffer = [duration, duration, duration, duration]
        else:
            gen_duration.buffer = [duration, duration]

    if len(gen_duration.buffer) > 0:
        # If we have something in the buffer, use it up first
        yield gen_duration.buffer.pop()
    else:
        yield duration


# Attach a 'buffer' to the generator function; this is the only way for it to
# remember data between yields
gen_duration.buffer = []


class ChordStrategy:
    """Strategy for selecting choices and weights for chords"""

    # 0 1 2 3 4 5 6 7 8 9 10 11 12
    # C | D | E F | G | A |  B  C

    # Tuple containing (root_shift, quality)
    chord_choices = [
        (0, "M"),
        (0, "sus2"),
        (0, "sus4"),
        (2, "m"),
        (2, "sus2"),
        (2, "sus4"),
        (4, "m"),
        (5, "M"),
        (5, "sus2"),
        (7, "M"),
        (7, "sus2"),
        (7, "sus4"),
        (9, "m"),
        (9, "sus2"),
        (9, "sus4"),
        (11, "d"),
    ]

    chord_weight_profiles = [
        # 000 222 3 44 777 999 e
        # Traditional, favor 1-4-5
        [50, 0, 0, 30, 0, 0, 30, 50, 0, 50, 0, 0, 30, 0, 0, 1],
        # More chance for other chords
        [50, 5, 5, 30, 5, 5, 30, 50, 5, 50, 5, 5, 30, 5, 5, 1],
        # Even more chance for other chords
        [50, 10, 10, 40, 10, 10, 40, 30, 10, 30, 10, 10, 40, 10, 10, 1],
        # Equal across the degrees, except diminished
        [10, 5, 5, 10, 5, 5, 10, 10, 5, 10, 5, 5, 10, 5, 5, 2],
    ]

    @classmethod
    def select_chord_profile(cls):
        """Select profile for picking chords"""

        cls.chord_weights = random.choice(cls.chord_weight_profiles)

    @classmethod
    def get_chord(cls):

        pick = random.choices(cls.chord_choices, weights=cls.chord_weights)[0]
        root_shift, quality = pick

        # Pick whether to turn into a 7th chord
        if random.choices([True, False], weights=(20, 80))[0]:
            if quality == "M" and root_shift != 7:
                suffix = "maj7"
            elif quality == "d":
                suffix = "min7dim5"  # To keep it in the key
            elif quality in ["sus2", "sus4"]:
                suffix = ""
                if (quality == "sus2" and root_shift in [2, 7, 9]) or (
                    quality == "sus4" and root_shift in [2, 4, 5, 9]
                ):
                    quality = "7{}".format(quality)
            else:
                suffix = "7"
            quality = "{}{}".format(quality, suffix)

        # Pick an inversion of the chord to use
        inversion = random.choice([0, 1, 2])

        return root_shift, quality, inversion


def get_pitches():
    """Get list of all pitches in the key"""

    key_template = [0, 2, 4, 5, 7, 9, 11]
    pitches = []
    for octave_note in range(0, 7 * 12 + 1, 12):
        pitches.extend([octave_note + n for n in key_template])

    return pitches


def chord_listing(chords):
    """Turn a list of chords into a string"""

    output = []
    for i, chord in enumerate(chords):
        output.append(f"|{chord.duration} {chord.name}".ljust(12))
        if (i + 1) % 4 == 0:
            output.append("\n".ljust(11))

    return "{}{}".format("".join(output).strip(), "\n")


class Piece:
    """Generatable piece of music"""

    # The version of this generative engine
    version = 11

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

        # Pick beats per measure
        self.beats_per_measure = random.choice([2, 3, 4, 5, 6, 7])
        print(f"Time signature: {self.beats_per_measure}/4")

        # Pick tempo
        self.default_tempo = random.randint(MIN_TEMPO, MAX_TEMPO)
        print(f"Tempo: {self.default_tempo}")

        # Select note duration profile
        duration_profile = NoteDurationStrategy.select_duration_profile()
        print(f"Note duration profile: {duration_profile}")

        # Select bass style
        self.bass_style = random.choice(["simple", "marco", "marching"])
        print(f"Bass style: {self.bass_style}")

        # Generate the song!
        structure = self.generate_structure()

        midi = self.create_track(
            {"name": "Chords", "instrument": instrument_2, "track": 1, "channel": 1},
            structure["chords"],
        )

        midi = self.create_track(
            {"name": "Bass", "instrument": instrument_3, "track": 2, "channel": 2},
            structure["bass"],
            midi=midi,
        )

        midi = self.create_track(
            {"name": "Melody", "instrument": instrument_1, "track": 0, "channel": 0},
            structure["melody"],
            midi=midi,
        )

        random.seed(None)

        return midi

    def generate_structure(self):
        """Plan out a structure for the song"""

        possible_sections = "abc"

        # Generate content in different sections
        sections = {}
        for label in possible_sections:
            sections[label] = {}

            ChordStrategy.select_chord_profile()

            measures = random.choice([2, 3, 4, 8])
            chords = self.generate_chords(measures)

            if measures < 5 and random.choice([True, False]):
                chords = chords + chords  # Double it up, but we'll get different melody

            sections[label]["chords"] = chords
            sections[label]["bass"] = self.generate_bass(chords)
            sections[label]["melody"] = self.generate_melody(chords)

        # Put together the sections in a pattern
        # E.g. aba, aabcbab, or abacab
        pattern = ["a"]  # Start with section a
        for _ in range(random.randint(2, 6)):
            pattern.append(random.choice(possible_sections))
            # Make sure all parts are represented
            if "b" not in pattern:
                pattern.insert(random.randint(1, len(pattern)), "b")
            if "c" not in pattern:
                pattern.insert(random.randint(1, len(pattern)), "c")

        print("Pattern: {}".format("".join(pattern)))

        print("-" * 60)
        structure = {"chords": [], "bass": [], "melody": []}
        for label in pattern:
            print(f"Section {label}", chord_listing(sections[label]["chords"]))
            structure["chords"].extend(sections[label]["chords"])
            structure["bass"].extend(sections[label]["bass"])
            structure["melody"].extend(sections[label]["melody"])

        # Ending
        chord = Chord(gm.NOTE_NUMS["C_2"], "M", duration=self.beats_per_measure)
        structure["chords"].append(chord)
        structure["bass"].append(Note(gm.NOTE_NUMS["C_2"] - 12, duration=1, volume=80))
        structure["melody"].append(
            Note(
                random.choice(chord.spread(clamp=True)).pitch + 12,
                duration=self.beats_per_measure,
                volume=100,
            )
        )
        print("Ending   ", chord_listing([chord]))
        print("-" * 60)

        return structure

    def generate_chords(self, measures=4):
        """Generate a chord progression"""

        root = gm.NOTE_NUMS["C_2"]

        time = 0
        chords = []
        for _ in range(0, measures):
            sub_measures = [self.beats_per_measure]

            if (
                self.beats_per_measure > 3
                and random.choices([True, False], weights=[10, 90])[0]
            ):
                # Split up measure into multiple chords
                if self.beats_per_measure == 4:
                    sub_measures = [2, 2]
                elif self.beats_per_measure == 5:
                    sub_measures = random.choice([[3, 2], [2, 3]])
                elif self.beats_per_measure == 6:
                    sub_measures = random.choice([[3, 3], [4, 2], [2, 4]])
                elif self.beats_per_measure == 7:
                    sub_measures = random.choice([[3, 4], [4, 3], [2, 2, 3], [3, 2, 2]])

            for chord_duration in sub_measures:
                # Pick which chord from the scale to use
                root_shift, quality, inversion = ChordStrategy.get_chord()

                chords.append(
                    Chord(
                        root + root_shift,
                        quality,
                        duration=chord_duration,
                        inversion=inversion,
                    )
                )

                time = time + chord_duration

        return chords

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

        # Select weighting for choosing how far the next pitch is
        self.interval_deltas = [0, 1, 2, 3, 4, 5]
        iv_weights_profiles = [
            (90, 80, 0, 0, 0, 0),  # Static
            (90, 50, 50, 5, 5, 10),  # Balanced
            (10, 10, 10, 10, 10, 10),  # Jumpy
        ]
        self.iv_weights = random.choice(iv_weights_profiles)

        # Select strategy for picking notes
        # First number is chance for using intervals to pick notes, second
        # number is chance to use a note from the chord only
        self.melodic_contour_strategy = random.choice([(100, 0), (50, 50), (20, 80)])

        notes_data = []
        for chord in chords:
            motive = self.generate_motive(chord, chord.duration)

            motive_duration = sum(n.duration for n in motive)
            if motive_duration > chord.duration:
                # Cut off last note to end at the measure
                up_to_last = sum(n.duration for n in motive[0:-1])
                motive[-1].duration = chord.duration - up_to_last

            notes_data.extend(motive)

        return notes_data

    def generate_motive(self, chord, length=4):
        """Generate a little motive around a root note"""

        volume = 100

        # Keep melody from getting too wild, high or low
        min_pitch = gm.NOTE_NUMS["C_2"]
        max_pitch = gm.NOTE_NUMS["C_5"]

        # Define the starting pitch
        pitch = chord.root + 12

        try:
            index = self.pitches.index(pitch)
        except ValueError:
            # Is an accidental; add it to the list of pitches?
            self.pitches.append(pitch)
            self.pitches.sort()
            index = self.pitches.index(pitch)

        notes_data = []
        time = 0
        max_time = time + length
        while time < max_time:
            # Choose a duration
            duration = next(gen_duration())

            # A rest or a note?
            if random.choices([True, False], weights=(100, 20))[0]:
                # Choose a new pitch
                if random.choices([True, False], weights=self.melodic_contour_strategy)[
                    0
                ]:
                    # Pick a pitch by moving by an interval along scale
                    interval = random.choices(
                        self.interval_deltas, weights=self.iv_weights
                    )[0]
                    if random.choice([True, False]):
                        # Up in pitch
                        pitch = self.pitches[index + interval]
                        if pitch > max_pitch:
                            pitch = pitch - 12
                    else:
                        # Down in pitch
                        pitch = self.pitches[index - interval]
                        if pitch < min_pitch:
                            pitch = pitch + 12
                else:
                    # Pick a pitch from the chord
                    chord_note = random.choice(chord.spread(clamp=True))
                    pitch = chord_note.pitch + 12  # An octave above

                # Add to list of notes
                notes_data.append(Note(pitch, duration, volume))
            else:
                # Add a rest
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
                midi.addText(track, onset_time, item.name)
                notes = item.spread(clamp=True)
                for note in notes:
                    add_note(onset_time, note)

            # Calculate when the next note/rest should start
            onset_time = onset_time + item.duration

        return midi


def main():

    sys.argv.pop(0)
    if len(sys.argv) > 0:
        # Use seed provided from command invocation
        seed = sys.argv[0]
    else:
        # Pick a random seed number
        seed = str(random.randint(0, 65535))

    piece = Piece()
    midi = piece.generate(seed)

    filename = f"song-v{Piece.version}-{seed}.mid"

    with open(filename, "wb") as output_file:
        midi.writeFile(output_file)

    print(f"Playing generated {filename}")
    play_music(filename)
    print("done.")


if __name__ == "__main__":
    main()
