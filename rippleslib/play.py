#!/usr/bin/env python3
"""Play midi file"""

import pygame
import sys

# Mixer config
freq = 44100
bitsize = -16  # unsigned 16 bit
channels = 2
buffer = 1024  # number of samples


def play_music(midi_filename):
    """Stream music_file in a blocking manner"""

    pygame.mixer.init(freq, bitsize, channels, buffer)
    pygame.mixer.music.set_volume(0.8)

    clock = pygame.time.Clock()
    pygame.mixer.music.load(midi_filename)
    pygame.mixer.music.play()

    # Listen for interruptions
    try:
        while pygame.mixer.music.get_busy():
            clock.tick(30)
    except KeyboardInterrupt as e:
        pygame.mixer.music.fadeout(1000)
        pygame.mixer.music.stop()
        raise SystemExit from e

    # Just some extra time before ending to let tails end
    for _ in range(8):
        clock.tick(30)


if __name__ == "__main__":

    sys.argv.pop(0)
    if len(sys.argv) > 0:
        midi_files = sys.argv
    else:
        midi_files = ["example.mid"]

    for midi_file in midi_files:
        print("Playing {}".format(midi_file))
        play_music(midi_file)

    print("done")

    pygame.quit()
    sys.stderr.close()
    sys.exit(0)
