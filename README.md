# Ripples

Generate random songs (midi format)

## Installation

This project uses python 3. Recommended set up:

```
python -m venv .venv
.venv/bin/activate
pip install -r requirements.txt
```

## Usage

To run, issue this command from the terminal:

```
./ripples
```

This will generate a random song, save it to a midi file and then play it.

You can pass in a string to provide a random seed to get the same song again
(run `./ripples <seed>`). Without passing in a seed it will randomly pick one.
It will display the seed it used so you can get the song again.

The midi file will be saved with the following file format:
`song-v{version}-{seed}.mid` If you like the output you can keep it and delete
the rest.

There is a script `play` that will play a midi file, just run
`./play <midi filename>` and it will play it.

## Methodology

The basic methodology of how it generates a song is it randomly decides on a
song structure (e.g. 'aabac') and then creates a chord progression and
generates a melody on top of that.

Thanks to Mark Conway Wirt for the midiutil package and the pygame team.
