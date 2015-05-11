import random
from pablo.analysis import estimate_main_band
from pydub import AudioSegment


def eq(track_file):
    """
    Guesses the main band for the track and applies a
    pass filter for that band.

    This kind of band analysis/EQing should _probably_ happen at
    the level of individual samples, and then we can separately
    assemble low/mid/high tracks.

    This could be smarter too - right now, if all tracks have the same band,
    well, too bad, you are probably going to be missing a frequency band in your song :(

    Mid-band tracks are unmanipulated.

    Tracks should be input as filenames to the bounced track files.

    Returns the modified track as an AudioSegment.

    This kinda sucks right now so not using it
    """
    band = estimate_main_band(track_file)
    segm = AudioSegment.from_file(track_file)

    if band == 'high':
        return segm.high_pass_filter(750)
    elif band == 'low':
        return segm.low_pass_filter(250)


def build_bar(samples, n):
    """
    Builds a bar of n beats in length,
    where n >= the shortest sample length.

        e.g. if the samples are cut into bars of 8, 16, 32,
        then n must be >= 8.

    Bars are constructed by selecting a sample of length n
    or by placing two adjacent bars of length n/2. This structure
    *should* produce more coherent (less spastic) tracks.

        e.g a bar of length 16 can be created by two samples of length 8
        or one sample of length 16, if available.

    A bar is returned as a list of samples.

    Samples should be input in the form:

        {
            'song name': {
                8:  [ ... samples ... ],
                16: [ ... samples ... ],
                ...
            },
            ...
        }
    """

    # Find samples of length n
    full_bar_samples = []
    sample_sizes = set()
    for song, chunk_groups in samples.items():
        full_bar_samples += chunk_groups.get(n, [])
        sample_sizes = sample_sizes.union(set(chunk_groups.keys()))

    if n < min(sample_sizes):
        raise Exception('Can\'t create a bar shorter than the shortest sample')

    # If this is the smallest sample size,
    # we can only return full bars.
    if n == min(sample_sizes):
        return [random.choice(full_bar_samples)]

    # Slightly favor complete bars, if available
    if full_bar_samples and random.random() <= 0.6:
        return [random.choice(full_bar_samples)]

    # Otherwise, assemble the bar from sub-bars.
    bar = []
    length = 0
    while length < n:
        bar += build_bar(samples, n/2)
        length += n/2

    return bar
