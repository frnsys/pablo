import os
import subprocess

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
        str(ratio)
    ])
    return outfile


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
    chunks = [beats[i:i + chunk_size] for i in range(0, len(beats), chunk_size)]
    chunks = [(c[0], c[-1]) for c in chunks]

    for i, (start, end) in enumerate(chunks):
        outfile = '{0}{1}.{2}'.format(prefix, i, format)
        outfile = os.path.join(outdir, outfile)
        outfiles.append( slice(infile, start, end, outfile) )

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
