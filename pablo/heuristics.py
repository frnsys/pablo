import random
from collections import defaultdict
from pablo.models.sample import Sample
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


def build_tracks(songs, length, n_tracks, coherent=True):
    """
    Builds multiple tracks so that samples from the same song
    are never playing simultaneously.
    """
    # Build the first track
    track = build_bar(songs, length, coherent=coherent)

    # Convert to a flattened list of slices
    track = sum([s.slices for s in track], ())

    tracks = [track]
    for i in range(n_tracks-1):
        track_ = build_bar(songs, length, coherent=coherent, tracks=tracks)
        track_ = sum([s.slices for s in track_], ())
        tracks.append(track_)

    return tracks


def build_bar(songs, n, prev_sample=None, coherent=True, tracks=[], bar_position=0):
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

    If `coherent=True`, Pablo will try to build _coherent_ bars:

        - higher probability that the same sample will be re-played
        - higher probability that the next sample in the sequence will be played
        - lower probability that the next sample will be from a different song

    This assumes that the samples are in their chronological sequence.
    That is, that samples i and i+1 for a song are temporally adjacent.

    Returns a list of Samples.
    """
    if len(tracks) >= len(songs):
        raise Exception('Must have more songs available than overlaid tracks')

    # Remove any songs which are simultaneously playing in other tracks.
    invalid_songs = []
    for track in tracks:
        invalid_songs.append(track[bar_position].song)
    songs = [s for s in songs if s not in invalid_songs]

    # Find samples of length n
    full_bar_samples = {}
    for song in songs:
        if n in song.sizes:
            full_bar_samples[song.name] = [s for s in song[n] if s is not None]

    min_size = min(s.min_size for s in songs)

    if n < min_size:
        raise Exception('Can\'t create a bar shorter than the shortest sample')

    # If this is the smallest sample size,
    # we can only return full bars.
    if n == min_size:
        if coherent:
            return _select_sample(full_bar_samples, n, prev_sample)
        else:
            song = random.choice(full_bar_samples.keys())
            return [random.choice(full_bar_samples[song])]

    # Slightly favor complete bars, if available
    if full_bar_samples and random.random() <= 0.6:
        if coherent:
            return _select_sample(full_bar_samples, n, prev_sample)
        else:
            song = random.choice(full_bar_samples.keys())
            return [random.choice(full_bar_samples[song])]

    # Otherwise, assemble the bar from sub-bars.
    bar = []
    length = 0
    while length < n:
        n_ = n/2
        bar += build_bar(songs, n_, prev_sample=prev_sample, bar_position=bar_position, tracks=tracks)
        bar_position += n_/min_size
        length += n_
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
        if random.random() <= 0.3:
            return [prev_sample]

        # Play the next chronological sample from the song (if available)
        if random.random() <= 0.75:
            next_sample = song.next_sample(prev_sample, length)
            if next_sample is not None:
                return [next_sample]

    # Otherwise, return a random sample from a random song
    # It's possible that some songs don't have samples to choose from
    song = random.choice([k for k in samples.keys() if samples[k]])
    return [random.choice(samples[song])]


def filter_slices(slices):
    """
    Filters slices to those that are of the most popular duration.

    The beat slicing slices slices of varying duration; even very slight variations
    will lead to beat slippage. So we compare sample durations and select only the
    duration with the most slices.

    I tried including slices from within a range of +- 0.05s of this duration and
    then time stretching them, but time stretching (at least with sox)
    is imprecise enough that it doesn't produce slices of the desired length.

    So we lose some of slices, but at least we don't have sneakers in the dryer.

    Slices should be input in the form:

        {
            song: [ <Slice>, ... ],
            ...
        }

    Returns a new dict of slices in the same form, just with
    inconsistently long or short slices replaced with None.
    This way the temporal adjacency structure of the slices is preserved,
    just with gaps.
    """

    # Group slices by sample size and duration
    durs = defaultdict(list)
    for song, slics in slices.items():
        for s in slics:
            dur = duration(s.file)
            durs[dur].append(s)

    # Identify the duration with the most slices
    best = max(durs.keys(), key=lambda d: len(durs[d]))

    # Remove the non-qualifying slices
    for song, slics in slices.items():
        slices[song] = [s if s in durs[best] else None for s in slics]

    return slices


def assemble_samples(samples):
    """
    Generates samples of the next largest size (n*2).

    Samples should be in the form:

        [ <Sample>, ... ]

    That is, each sample should be represented as a tuple of its constituent samples.

    This iterates over samples as non-overlapping pairs,
    adding a complete tuple if the pair consists of
    two present samples or None otherwise.
    """
    # Assuming samples are of the same length
    # and from the same song (they should be)
    samp = next((s for s in samples if s is not None), None)

    # If this is None, that means no slices
    # successfully made it through filtering
    if samp is None:
        return [None for _ in samples]

    n = samp.size * 2
    song = samp.song

    larger_samples = []
    for i, (s1, s2) in enumerate(zip(samples[::2], samples[1::2])):
        if s1 is None or s2 is None:
            larger_samples.append(None)
        else:
            sample = Sample(s1.slices + s2.slices, song, n, i)
            larger_samples.append(sample)

    return larger_samples
