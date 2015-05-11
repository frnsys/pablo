"""
I don't really understand any of this, most
of this is adapted from Essentia's examples.
The Essentia python bindings are really unintuitive.
"""

import numpy as np
from pablo.key import Key
from pablo.datastore import save, load
from essentia import Pool, run, standard, streaming


def analyze(infile):
    """
    Performs the required analysis on an audio file.
    Will try to load an existing analysis based on the file's hash;
    otherwise, will save the analysis when it's done.
    """
    data = load(infile)
    if data is not None:
        bpm, key, scale = data
        return bpm, Key(key, scale)

    bpm = estimate_bpm(infile)
    key = estimate_key(infile)
    save(infile, bpm, key)

    return bpm, key


def estimate_bpm(infile):
    """
    Estimates the BPM for an audio file.
    """
    pool = Pool()

    loader = streaming.MonoLoader(filename=infile)
    bt = streaming.RhythmExtractor2013()
    bpm_histogram = streaming.BpmHistogramDescriptors()
    centroid = streaming.Centroid(range=250) # BPM histogram output size is 250

    loader.audio >> bt.signal
    bt.bpm >> (pool, 'bpm')
    bt.ticks >> None
    bt.confidence >> None
    bt.estimates >> None
    bt.bpmIntervals >> bpm_histogram.bpmIntervals
    bpm_histogram.firstPeakBPM >> (pool, 'bpm_first_peak')
    bpm_histogram.firstPeakWeight >> None
    bpm_histogram.firstPeakSpread >> None
    bpm_histogram.secondPeakBPM >> (pool, 'bpm_second_peak')
    bpm_histogram.secondPeakWeight >> None
    bpm_histogram.secondPeakSpread >> None
    bpm_histogram.histogram >> (pool, 'bpm_histogram')
    bpm_histogram.histogram >> centroid.array
    centroid.centroid >> (pool, 'bpm_centroid')

    run(loader)
    return pool['bpm']


def estimate_key(infile):
    """
    Estimates the key and scale for an audio file.
    """
    loader = streaming.MonoLoader(filename=infile)
    framecutter = streaming.FrameCutter()
    windowing = streaming.Windowing(type="blackmanharris62")
    spectrum = streaming.Spectrum()
    spectralpeaks = streaming.SpectralPeaks(orderBy="magnitude",
                                magnitudeThreshold=1e-05,
                                minFrequency=40,
                                maxFrequency=5000,
                                maxPeaks=10000)
    pool = Pool()
    hpcp = streaming.HPCP()
    key = streaming.Key()

    loader.audio >> framecutter.signal
    framecutter.frame >> windowing.frame >> spectrum.frame
    spectrum.spectrum >> spectralpeaks.spectrum
    spectralpeaks.magnitudes >> hpcp.magnitudes
    spectralpeaks.frequencies >> hpcp.frequencies
    hpcp.hpcp >> key.pcp
    key.key >> (pool, 'tonal.key_key')
    key.scale >> (pool, 'tonal.key_scale')
    key.strength >> (pool, 'tonal.key_strength')

    run(loader)

    return Key(pool['tonal.key_key'], pool['tonal.key_scale'])



def estimate_beats(infile):
    """
    Return the estimated beat onsets in seconds for an audio file.
    """
    audio = standard.MonoLoader(filename=infile)()
    bt = standard.BeatTrackerMultiFeature()
    beats, _ = bt(audio)
    return beats


def estimate_main_band(infile):
    """
    Estimate if this is a low, mid, or high track.

    Not _really_ sure if this does what I need it to,
    but some quick tests looked right.
    """
    loader = streaming.MonoLoader(filename=infile)
    framecutter = streaming.FrameCutter()
    windowing = streaming.Windowing(type="blackmanharris62")
    spectrum = streaming.Spectrum()
    freqbands = streaming.FrequencyBands(frequencyBands=[0, 250, 750, 4000])
    pool = Pool()

    loader.audio >> framecutter.signal
    framecutter.frame >> windowing.frame >> spectrum.frame
    spectrum.spectrum >> freqbands.spectrum
    freqbands.bands >> (pool, 'bands')

    run(loader)

    sums = np.sum(pool['bands'], axis=0)
    band = np.argmax(sums)
    if band == 0:
        return 'low'
    elif band == 1:
        return 'mid'
    elif band == 2:
        return 'high'
