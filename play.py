"""Play midi file"""

import pygame


def play_music(midi_filename):
    """Stream music_file in a blocking manner"""

    clock = pygame.time.Clock()
    pygame.mixer.music.load(midi_filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        clock.tick(30)  # check if playback has finished


midi_file = "example.mid"

# Mixer config
freq = 44100
bitsize = -16  # unsigned 16 bit
channels = 2
buffer = 1024  # number of samples
pygame.mixer.init(freq, bitsize, channels, buffer)

# Optional volume 0 to 1.0
pygame.mixer.music.set_volume(0.8)

# Listen for interruptions
try:
    play_music(midi_file)
except KeyboardInterrupt as e:
    # if user hits Ctrl/C then exit
    # (works only in console mode)
    pygame.mixer.music.fadeout(1000)
    pygame.mixer.music.stop()
    raise SystemExit from e
