import random
import shutil
from itertools import chain
from collections import defaultdict
from pablo.analysis import estimate_main_band, duration
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


def build_bar(samples, n, prev_sample=None, coherent=True):
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
                8:  [(sample,), ...],
                16: [(sample, sample), ...],
                ...
            },
            ...
        }

    If `coherent=True`, Pablo will try to build _coherent_ bars:

        - higher probability that the same sample will be re-played
        - higher probability that the next sample in the sequence will be played
        - lower probability that the next sample will be from a different song

    This assumes that the samples are in their chronological sequence.
    That is, that samples i and i+1 for a song are temporally adjacent.

    Returns a list of Samples.
    """

    # Find samples of length n
    sample_sizes = set()
    full_bar_samples = defaultdict(list)
    for song, chunk_groups in samples.items():
        samps = chunk_groups.get(n, [])
        if samps:
            full_bar_samples[song] += [Sample(s, song, n, i) for i, s in enumerate(samps) if s is not None]
        sample_sizes = sample_sizes.union(set(chunk_groups.keys()))

    if n < min(sample_sizes):
        raise Exception('Can\'t create a bar shorter than the shortest sample')

    # If this is the smallest sample size,
    # we can only return full bars.
    if n == min(sample_sizes):
        if coherent:
            return _select_sample(full_bar_samples, n, prev_sample)
        else:
            song = random.choice(samples.keys())
            return [random.choice(samples[song])]

    # Slightly favor complete bars, if available
    if full_bar_samples and random.random() <= 0.6:
        if coherent:
            return _select_sample(full_bar_samples, n, prev_sample)
        else:
            song = random.choice(samples.keys())
            return [random.choice(samples[song])]

    # Otherwise, assemble the bar from sub-bars.
    bar = []
    length = 0
    while length < n:
        bar += build_bar(samples, n/2, prev_sample=prev_sample)
        length += n/2
        prev_sample = bar[-1]

    return bar


def _select_sample(samples, length, prev_sample):
    """
    Selects a sample via a markov chain

    Samples should be in the form:

        {
            'song_name': [ ... samples ... ],
            ...
        }
    """
    if prev_sample is not None:
        song = prev_sample.song

        # Repeat the sample
        if random.random() <= 0.6:
            return [prev_sample]

        # The previous sample may be of a different length than
        # the current one, so convert its index.
        nidx = (prev_sample.length/length * prev_sample.index) + 1
        if len(samples[song]) > nidx and random.random() <= 0.5:
            # Play the next chronological sample from the song
            return [samples[song][nidx]]

    # Otherwise, return a random sample from a random song
    song = random.choice(samples.keys())
    return [random.choice(samples[song])]


def filter_samples(samples):
    """
    Filters samples to those that are of the most popular duration.

    The beat slicing slices samples of varying duration; even very slight variations
    will lead to beat slippage. So we compare sample durations and select only the
    duration with the most samples.

    I tried including samples from within a range of +- 0.05s of this duration and
    then time stretching them, but time stretching (at least with sox)
    is imprecise enough that it doesn't produce samples of the desired length.

    So we lose some of samples, but at least we don't have sneakers in the dryer.

    Samples should be input in the form:

        {
            'song name': [ ... samples ... ],
            ...
        }

    Returns a new dict of samples in the same form, just with
    inconsistently long or short samples replaced with None.
    This way the temporal adjacency structure of the samples is preserved,
    just with gaps.
    """

    # Group samples by sample size and duration
    durs = defaultdict(list)
    for song, samps in samples.items():
        for s in samps:
            dur = duration(s)
            durs[dur].append(s)

    # Identify the duration with the most samples
    best = max(durs.keys(), key=lambda d: len(durs[d]))

    # Remove the non-qualifying samples
    for song, samps in samples.items():
        samples[song] = [s if s in durs[best] else None for s in samps]

    return samples


def assemble_samples(samples):
    """
    Generates samples of the next largest size (n*2).

    Samples should be in the form:

        [(sample,), ...]

    That is, each sample should be represented as a tuple of its constituent samples.

    This iterates over samples as non-overlapping pairs,
    adding a complete tuple if the pair consists of
    two present samples or None otherwise.
    """

    larger_samples = []
    for s1, s2 in zip(samples[::2], samples[1::2]):
        if s1 is None or s2 is None:
            larger_samples.append(None)
        else:
            larger_samples.append(s1 + s2)

    return larger_samples



class Sample():
    def __init__(self, parts, song, length, index):
        self.parts = parts
        self.song = song
        self.length = length
        self.index = index
