import os
import subprocess
from essentia import standard

try:
    from subprocess import DEVNULL
except ImportError:
    DEVNULL = open(os.devnull, 'wb')


def tempo_stretch(infile, from_bpm, to_bpm, outfile):
    ratio = to_bpm/from_bpm
    subprocess.call([
        'sox',
        infile,
        outfile,
        'tempo',
        '-m',
        str(ratio)
    ])
    return outfile


def time_stretch(infile, from_time, to_time, outfile):
    return tempo_stretch(infile, from_time, to_time, outfile)


def key_shift(infile, from_key, to_key, outfile):
    semitones = from_key.distance(to_key)
    cents = semitones * 100
    subprocess.call([
        'sox',
        infile,
        outfile,
        'pitch',
        str(cents)
    ])
    return outfile


def beat_slice(infile, beats, chunk_size, outdir, prefix='', format='mp3'):
    outfiles = []
    format = format.strip('.')
    chunks = [beats[i:i + chunk_size] for i in range(0, len(beats), chunk_size)]
    chunks = [(c[0], c[-1]) for c in chunks]

    for i, (start, end) in enumerate(chunks):
        outfile = '{0}{1}.{2}'.format(prefix, i, format)
        outfile = os.path.join(outdir, outfile)
        outfile = slice(infile, start, end, outfile)

        # Sometimes the file isn't saved?
        if os.path.exists(outfile):
            outfiles.append(outfile)

    return outfiles


def slice(infile, start, end, outfile):
    subprocess.call([
        'ffmpeg',
        '-i',
        infile,
        '-ss',
        str(start),
        '-to',
        str(end),
        outfile
    ], stdout=DEVNULL, stderr=DEVNULL)
    return outfile


def trim_silence(infile, outfile):
    """
    Remove silence from the beginning of a song.
    <http://digitalcardboard.com/blog/2009/08/25/the-sox-of-silence/>
    """
    subprocess.call([
        'sox',
        infile,
        outfile,
        'silence',
        '1',
        '0.1',
        '1%'
    ])
    return outfile


def add_click(infile, beats, outfile):
    """
    Adds a click track to a song according to the specified beats.

    This is used for debugging beat alignment.
    """
    audio = standard.MonoLoader(filename=infile)()
    marker = standard.AudioOnsetsMarker(onsets=beats, type='beep')
    marked_audio = marker(audio)
    standard.MonoWriter(filename=outfile)(marked_audio)


def vocal_eq(infile, outfile):
    """
    Tries to EQ a song so that vocals are more prominent.
    Doesn't work very well.
    """
    subprocess.call([
        'sox',
        infile,
        outfile,
        'bass',
        '-32',
        '200',
        'vad',
        'norm'
    ])
    return outfile
