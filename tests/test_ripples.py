"""Unit tests for ripples lib"""

import random
import sys
from os.path import dirname, realpath

import unittest
from unittest.mock import patch

# Gotta do this nonsense to force the rippleslib to find its modules during testing
sys.path.append(dirname(dirname(realpath(__file__))) + "/rippleslib")

# pylint: disable=wrong-import-position
from rippleslib import ripples


class TestRipples(unittest.TestCase):
    """Test notes, chords"""

    def test_note_object(self):
        note = ripples.Note(60)
        self.assertEqual(60, note.pitch)
        self.assertEqual("<Note C_3 quarter 100>", str(note))

        # Test each duration symbol
        note = ripples.Note(60, duration=4)
        self.assertEqual("<Note C_3 whole 100>", str(note))
        self.assertEqual("C_3", note.name)
        self.assertEqual("C", note.note_class)

        note = ripples.Note(60, duration=2)
        self.assertEqual("<Note C_3 half 100>", str(note))

        note = ripples.Note(60, duration=1.5)
        self.assertEqual("<Note C_3 quarter dot 100>", str(note))

        note = ripples.Note(60, duration=1)
        self.assertEqual("<Note C_3 quarter 100>", str(note))

        note = ripples.Note(60, duration=0.75)
        self.assertEqual("<Note C_3 8th dot 100>", str(note))

        note = ripples.Note(60, duration=0.5)
        self.assertEqual("<Note C_3 8th 100>", str(note))

        note = ripples.Note(60, duration=0.25)
        self.assertEqual("<Note C_3 16th 100>", str(note))

        # Something else means it could be represented as more than one note with a tie
        note = ripples.Note(60, duration=3)
        self.assertEqual("<Note C_3 tie dur:3 100>", str(note))

        # Repr
        self.assertEqual("<Note C_3 tie dur:3 100>", repr(note))

    def test_note_limits(self):
        # Below allowed note numbers should result in the min 0
        note = ripples.Note(-1)
        self.assertEqual(0, note.pitch)
        self.assertEqual("<Note C_-2 quarter 100>", str(note))

        # Above allowed note numbers should result in the max 127
        note = ripples.Note(128)
        self.assertEqual(127, note.pitch)
        self.assertEqual("<Note G_8 quarter 100>", str(note))

    def test_rest(self):
        rest = ripples.Rest()
        self.assertEqual(1, rest.duration)

        rest = ripples.Rest(4)
        self.assertEqual(4, rest.duration)
        self.assertEqual("<Rest whole>", str(rest))

        rest = ripples.Rest(3)
        self.assertEqual(3, rest.duration)
        self.assertEqual("<Rest tie dur:3>", str(rest))

        # Repr
        self.assertEqual("<Rest tie dur:3>", repr(rest))

    def test_chord(self):
        chord = ripples.Chord(48)
        self.assertEqual(48, chord.root)
        self.assertEqual("<Chord CM (i0)>", str(chord))
        self.assertEqual("<Chord CM (i0)>", repr(chord))
        self.assertEqual("CM", chord.name)

        spread = chord.spread()
        self.assertEqual([48, 52, 55], [n.pitch for n in spread])

    def test_chord_quality(self):
        chord = ripples.Chord(48, "m")
        self.assertEqual("Cm", chord.name)

        spread = chord.spread()
        self.assertEqual(["C_2", "D#_2", "G_2"], [n.name for n in spread])

    def test_chord_clamp(self):
        chord = ripples.Chord(36)
        spread = chord.spread(True)
        self.assertEqual(["C_2", "E_2", "G_2"], [n.name for n in spread])

        chord = ripples.Chord(84)
        spread = chord.spread(True)
        self.assertEqual(["C_4", "E_4", "G_4"], [n.name for n in spread])

    def test_chord_inversions(self):
        chord = ripples.Chord(60, inversion=1)
        spread = chord.spread()
        self.assertEqual(["C_4", "E_3", "G_3"], [n.name for n in spread])

        chord = ripples.Chord(60, inversion=2)
        spread = chord.spread()
        self.assertEqual(["C_4", "E_4", "G_3"], [n.name for n in spread])

        chord = ripples.Chord(60, inversion=2)
        spread = chord.spread(clamp=True)
        self.assertEqual(["C_3", "E_3", "G_2"], [n.name for n in spread])

    def test_get_durations(self):
        # Deterministic which one will be picked
        random.seed("111")
        profile = ripples.NoteDurationStrategy.select_duration_profile()
        random.seed(None)

        self.assertEqual("balanced", profile)

    def test_gen_duration(self):
        # Deterministic which one will be picked
        random.seed("111")
        ripples.NoteDurationStrategy.select_duration_profile()

        value = next(ripples.gen_duration())
        self.assertEqual(0.25, value)

        # Next one should be a 16th note too
        value = next(ripples.gen_duration())
        self.assertEqual(0.25, value)

        # And the next one should be a 16th note too
        value = next(ripples.gen_duration())
        self.assertEqual(0.25, value)

        # ...and the next one should be a 16th note too
        value = next(ripples.gen_duration())
        self.assertEqual(0.25, value)

        # This one is a half-note
        value = next(ripples.gen_duration())
        self.assertEqual(2, value)
        random.seed(None)

    @patch("ripples.print")
    def test_generate_piece(self, mock_print):
        mock_print.return_value = None
        piece = ripples.Piece()
        result = piece.generate("222")

        print(result)


if __name__ == "__main__":
    unittest.main()
