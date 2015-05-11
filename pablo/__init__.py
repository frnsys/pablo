import essentia
essentia.log.warningActive = False

import os
import click
import shutil
import random
from glob import glob
from colorama import Fore
from pablo import analysis, manipulate
from pydub import AudioSegment


formats = ['mp3', 'wav']


@click.group()
def cli():
    pass


def echo(tmp, *txts, **kwargs):
    color = kwargs.get('color', Fore.GREEN)
    txts = ['{0}{1}{2}'.format(color, txt, Fore.RESET) for txt in txts]
    print(tmp.format(*txts))


@cli.command()
@click.argument('library', type=click.Path(exists=True))
def analyze(library):
    """
    Analyze all songs in a directory.

    Their analyses will be persisted to a local db.
    """
    files = []
    for fmt in formats:
        files += glob(os.path.join(library, '*.{0}'.format(fmt)))

    echo('Analyzing {0} songs...', len(files))
    with click.progressbar(files) as bar:
        for f in bar:
            analysis.analyze(f)


@cli.command()
@click.argument('library', type=click.Path(exists=True))
@click.argument('outdir', type=click.Path())
@click.option('-C', 'chunk_sizes', default=[8,16,32], help='The chunk sizes to generate samples with. Should be a power of 2', type=list)
@click.option('-T', 'n_tracks', default=2, help='The number of tracks to produce and mix together', type=int)
@click.option('-S', 'n_songs', default=None, help='The number of songs to include (if enough are available)', type=int)
@click.option('-M', 'n_samples', default=10, help='The number of samples to use for each track', type=int)
def mix(library, outdir, chunk_sizes, n_tracks, n_songs, n_samples):
    # Prepare output directory, just to check if the directory is not empty
    outdir = os.path.join(outdir, 'pablo_mix')
    sample_dir = os.path.join(outdir, 'samples')
    if os.path.exists(outdir) and os.listdir(outdir):
        raise Exception('Output directory is not empty')
    os.makedirs(sample_dir)

    echo('Using library at {0}', library, color=Fore.CYAN)

    files = []
    for fmt in formats:
        files += glob(os.path.join(library, '*.{0}'.format(fmt)))

    echo('Working with {0} songs', len(files))

    # Select a song to base the mix around
    random.shuffle(files)
    focal = files.pop()
    focal_bpm, focal_key = analysis.analyze(focal)

    echo('\nFocal song: {0}', focal, color=Fore.YELLOW)
    echo('\tBPM: {0}', focal_bpm)
    echo('\tKey: {0} ({1})', focal_key.key, focal_key.scale)

    # Search for songs that require relatively small modifications
    # to match the focal song
    bpm_range_l = 0.85 * focal_bpm
    bpm_range_u = 1.15 * focal_bpm
    key_range = 3

    # Select appropriate songs to mix
    n = n_songs if n_songs is not None else random.randint(4, 10)
    selections = []
    echo('\nSelecting {0} other songs', n)

    while len(selections) < n and files:
        song = files.pop()
        bpm, key = analysis.analyze(song)
        echo('Analyzing {0}', song, color=Fore.CYAN)
        if bpm_range_l <= bpm <= bpm_range_u and (focal_key.mixable(key) or abs(focal_key.distance(key)) <= key_range):
            echo('\t{0}', 'OK')
            selections.append((song, bpm, key))
        else:
            echo('\tSkipping')

    # Manipulate songs as needed and generate samples
    echo('\n{0}', 'Processing songs', color=Fore.YELLOW)
    samples = []
    for song, bpm, key in selections + [(focal, focal_bpm, focal_key)]:
        filename = os.path.basename(song)
        name, ext = os.path.splitext(filename)
        echo('Processing {0}', filename, color=Fore.CYAN)

        # Copy over files
        outfile = os.path.join(outdir, filename)
        shutil.copy(song, outfile)
        tmpfile = os.path.join(outdir, '{0}.tmp{1}'.format(name, ext))

        # Process as necessary
        if not focal_key.mixable(key):
            echo('\tChanging key')
            manipulate.key_shift(outfile, key, focal_key, tmpfile)
            shutil.move(tmpfile, outfile)

        if focal_bpm != bpm:
            echo('\tChanging bpm')
            manipulate.tempo_stretch(outfile, bpm, focal_bpm, tmpfile)
            shutil.move(tmpfile, outfile)

        # Slice according to beats
        echo('\tSlicing')
        beats = analysis.estimate_beats(outfile)
        for chunk_size in chunk_sizes:
            prefix = '{0}_{1}_'.format(name, chunk_size)
            samples += manipulate.beat_slice(outfile,
                                             beats,
                                             chunk_size,
                                             sample_dir,
                                             prefix=prefix,
                                             format=ext)

    # Select samples and assemble tracks
    echo('\n{0}', 'Assembling tracks', color=Fore.YELLOW)
    tracks = []
    tracklist = []
    for i in range(n_tracks):
        selected = random.sample(samples, n_samples)
        sounds = [AudioSegment.from_file(f) for f in selected]
        track = sounds[0].normalize()
        for sound in sounds[1:]:
            # Remove crossfade to keep timing right? Not sure if necessary
            track = track.append(sound.normalize(), crossfade=0)
        tracks.append(track)

        track_file = os.path.join(outdir, 'track_{0}.mp3'.format(i))
        track.export(track_file, format='mp3')

        tracklist.append([os.path.basename(s) for s in selected])

    # Overlay the tracks
    echo('\n{0}', 'Assembling mix', color=Fore.YELLOW)
    out_mix = tracks[0]
    for track in tracks[1:]:
        out_mix = out_mix.overlay(track)

    # Save the mix
    mix_file = os.path.join(outdir, '_mix.mp3')
    out_mix.export(mix_file, format='mp3')

    # Write the tracklist
    tracklisting = '\n\n---\n\n'.join(['\n'.join(tl) for tl in tracklist])
    trl_file = os.path.join(outdir, '_tracklist.txt')
    with open(trl_file, 'w') as f:
        f.write(tracklisting)

    echo('\n{0}', 'Done')
