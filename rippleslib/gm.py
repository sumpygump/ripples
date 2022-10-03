"""General MIDI Constants"""

# --------------------------------------------------------------
# General MIDI Note Numbers / Note Names
# --------------------------------------------------------------

# Names of the midi note numbers for values 0-127
# E.g. `NOTE_NAMES[60] => "C_3"`
# E.g. `NOTE_CLASS[60] => "C"` # Note class is the note name without the octave
note_template = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
NOTE_NAMES = []
NOTE_CLASS = []
for octave in range(-2, 9):
    NOTE_CLASS.extend(list(note_template))
    NOTE_NAMES.extend([f"{n}_{octave}" for n in note_template])

# Midi note numbers for the names
# E.g. `NOTE_NUMS["C_3"] => 60`
NOTE_NUMS = {}
for value, name in enumerate(NOTE_NAMES):
    NOTE_NUMS[name] = value

# --------------------------------------------------------------
# General MIDI Instruments / Programs
# --------------------------------------------------------------
# List of GM programs (instruments), as outlined in General MIDI
# https://en.wikipedia.org/wiki/General_MIDI
# --------------------------------------------------------------

# Piano
ACOUSTIC_GRAND_PIANO = 0
BRIGHT_ACOUSTIC_PIANO = 1
ELECTRIC_GRAND_PIANO = 2
HONKY_TONK_PIANO = 3
ELECTRIC_PIANO_1 = 4  # Usually a rhodes
ELECTRIC_PIANO_2 = 5  # Usually an FM piano
HARPSICHORD = 6
CLAVINET = 7

PIANO_SET = list(range(ACOUSTIC_GRAND_PIANO, CLAVINET + 1))

# Chromatic Percussion
CELESTA = 8
GLOCKENSPIEL = 9
MUSIC_BOX = 10
VIBRAPHONE = 11
MARIMBA = 12
XYLOPHONE = 13
TUBULAR_BELLS = 14
DULCIMER = 15

CHROMATIC_PERCUSSION_SET = list(range(CELESTA, DULCIMER + 1))

# Organ
DRAWBAR_ORGAN = 16
PERCUSSIVE_ORGAN = 17
ROCK_ORGAN = 18
CHURCH_ORGAN = 19
REED_ORGAN = 20
ACCORDION = 21
HARMONICA = 22
TANGO_ACCORDION = 23

ORGAN_SET = list(range(DRAWBAR_ORGAN, TANGO_ACCORDION + 1))

# Guitar
ACOUSTIC_GUITAR_NYLON = 24
ACOUSTIC_GUITAR_STEEL = 25
ELECTRIC_GUITAR_JAZZ = 26
ELECTRIC_GUITAR_CLEAN = 27
ELECTRIC_GUITAR_MUTED = 28
ELECTRIC_GUITAR_OVERDRIVEN = 29
ELECTRIC_GUITAR_DISTORTION = 30
ELECTRIC_GUITAR_HARMONICS = 31

GUITAR_SET = list(range(ACOUSTIC_GUITAR_NYLON, ELECTRIC_GUITAR_HARMONICS + 1))

# Bass
ACOUSTIC_BASS = 32
ELECTRIC_BASS_FINGER = 33
ELECTRIC_BASS_PICKED = 34
FRETLESS_BASS = 35
SLAP_BASS_1 = 36
SLAP_BASS_2 = 37
SYNTH_BASS_1 = 38
SYNTH_BASS_2 = 39

BASS_SET = list(range(ACOUSTIC_BASS, SYNTH_BASS_2 + 1))

# Strings
VIOLIN = 40
VIOLA = 41
CELLO = 42
CONTRABASS = 43
TREMOLO_STRINGS = 44
PIZZICATO_STRINGS = 45
ORCHESTRAL_HARP = 46
TIMPANI = 47

STRINGS_SET = list(range(VIOLIN, TIMPANI + 1))

# Ensemble
STRING_ENSEMBLE_1 = 48
STRING_ENSEMBLE_2 = 49
SYNTH_STRINGS_1 = 50
SYNTH_STRINGS_2 = 51
CHOIR_AAHS = 52
VOICE_OOHS = 53
SYNTH_VOICE = 54  # or solo vox
ORCHESTRA_HIT = 55

ENSEMBLE_SET = list(range(STRING_ENSEMBLE_1, ORCHESTRA_HIT + 1))

# Brass
TRUMPET = 56
TROMBONE = 57
TUBA = 58
MUTED_TRUMPET = 59
FRENCH_HORN = 60
BRASS_SECTION = 61
SYNTH_BRASS_1 = 62
SYNTH_BRASS_2 = 63

BRASS_SET = list(range(TRUMPET, SYNTH_BRASS_2 + 1))

# Reed
SOPRANO_SAX = 64
ALTO_SAX = 65
TENOR_SAX = 66
BARITONE_SAX = 67
OBOE = 68
ENGLISH_HORN = 69
BASSOON = 70
CLARINET = 71

REED_SET = list(range(SOPRANO_SAX, CLARINET + 1))

# Pipe
PICCOLO = 72
FLUTE = 73
RECORDER = 74
PAN_FLUTE = 75
BLOWN_BOTTLE = 76
SHAKUHACHI = 77
WHISTLE = 78
OCARINA = 79

PIPE_SET = list(range(PICCOLO, OCARINA + 1))

# Synth Lead
LEAD_1 = 80  # Square
LEAD_2 = 81  # Sawtooth
LEAD_3 = 82  # Calliope
LEAD_4 = 83  # Chiff
LEAD_5 = 84  # Charang, a guitar-like lead
LEAD_6 = 85  # Space voice
LEAD_7 = 86  # Fifths
LEAD_8 = 87  # Bass and lead

LEAD_SQUARE = 80
LEAD_SAW = 81
LEAD_CALLIOPE = 82
LEAD_CHIFF = 83
LEAD_CHARANG = 84
LEAD_SPACE = 85
LEAD_FIFTHS = 86
LEAD_BASS_AND_LEAD = 87

LEAD_SET = list(range(LEAD_1, LEAD_8 + 1))

# Synth Pad
PAD_1 = 88  # New age or Fantasia, a warm pad stacked with a bell
PAD_2 = 89  # Warm
PAD_3 = 90  # Polysynth
PAD_4 = 91  # Choir
PAD_5 = 92  # Bowed glass or bowed
PAD_6 = 93  # Metallic
PAD_7 = 94  # Halo
PAD_8 = 95  # Sweep

PAD_FANTASIA = 88
PAD_WARM = 89
PAD_POLYSYNTH = 90
PAD_CHOIR = 91
PAD_BOWED = 92
PAD_METALLIC = 93
PAD_HALO = 94
PAD_SWEEP = 95

PAD_SET = list(range(PAD_1, PAD_8 + 1))

# Synth Effects
FX_1 = 96  # Rain
FX_2 = 97  # Soundtrack, a bright perfect fifth pad
FX_3 = 98  # Crystal
FX_4 = 99  # Atmosphere, usually a nylon-like sound
FX_5 = 100  # Brightness
FX_6 = 101  # Goblins
FX_7 = 102  # Echoes or echo drops
FX_8 = 103  # Sci-fi or star theme

FX_RAIN = 96
FX_SOUNDTRACK = 97
FX_CRYSTAL = 98
FX_ATMOSPHERE = 99
FX_BRIGHTNESS = 100
FX_GOBLINS = 101
FX_ECHOES = 102
FX_SCI_FI = 103

FX_SET = list(range(FX_1, FX_8 + 1))

# Ethnic
SITAR = 104
BANJO = 105
SHAMISEN = 106
KOTO = 107
KALIMBA = 108
BAG_PIPE = 109
FIDDLE = 110
SHANAI = 111

ETHNIC_SET = list(range(SITAR, SHANAI + 1))

# Percussive
TINKLE_BELL = 112
AGOGO = 113
STEEL_DRUMS = 114
WOODBLOCK = 115
TAIKO_DRUM = 116
MELODIC_TOM = 117
SYNTH_DRUM = 118
REVERSE_CYMBAL = 119

PERCUSSIVE_SET = list(range(TINKLE_BELL, REVERSE_CYMBAL + 1))

# Sound Effects
GUITAR_FRET_NOISE = 120
BREATH_NOISE = 121
SEASHORE = 122
BIRD_TWEET = 123
TELEPHONE_RING = 124
HELICOPTER = 125
APPLAUSE = 126
GUNSHOT = 127

SOUND_FX_SET = list(range(GUITAR_FRET_NOISE, GUNSHOT + 1))

ALL_LEAD_LIKE_SET = (
    PIANO_SET
    + CHROMATIC_PERCUSSION_SET
    + ORGAN_SET
    + GUITAR_SET
    + STRINGS_SET
    + BRASS_SET
    + REED_SET
    + PIPE_SET
    + LEAD_SET
    + ETHNIC_SET
)

ALL_ACCOMPANIMENT_SET = ORGAN_SET + ENSEMBLE_SET + PAD_SET
