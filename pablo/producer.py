import os
from pablo import heuristics, analysis
from pydub import AudioSegment


def produce_tracks(samples, outdir, length=256, coherent=True, n_tracks=2):
    """
    Generate some tracks from the given samples.
    """
    tracks = []
    tracklist = []

    for i in range(n_tracks):
        selected = [s.parts for s in heuristics.build_bar(samples, length, coherent=coherent)]

        # Flatten
        files = sum(selected, ())

        sounds = [AudioSegment.from_file(f) for f in files]
        track = sounds[0].normalize()
        for sound in sounds[1:]:
            # Remove crossfade to keep timing right? Not sure if necessary
            track = track.append(sound.normalize(), crossfade=15)

        track_file = os.path.join(outdir, 'track_{0}.mp3'.format(i))
        track.export(track_file, format='mp3')
        tracks.append(track)

        time = 0
        timeline = []
        for f in files:
            timeline.append((time, os.path.basename(f)))
            time += analysis.duration(f)
        tracklist.append(timeline)

    return tracks, tracklist


def produce_mix(tracks, outfile, format='mp3'):
    """
    Mix a list of tracks together.
    """
    mix = tracks[0]
    for track in tracks[1:]:
        mix = mix.overlay(track)

    # Save the mix
    mix.export(outfile, format=format)
