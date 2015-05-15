import os
from pablo import heuristics, analysis
from pydub import AudioSegment


def produce_tracks(songs, outdir, length=256, coherent=True, n_tracks=2):
    """
    Generate some tracks from the given Songs.
    """
    tracks = []
    tracklist = []

    for i, slices in enumerate(heuristics.build_tracks(songs, length, n_tracks, coherent=coherent)):
        files = [slice.file for slice in slices]
        sounds = [AudioSegment.from_file(f) for f in files]

        # Create the track audio
        track = sounds[0].normalize()
        for sound in sounds[1:]:
            # Remove crossfade to keep timing right? Not sure if necessary
            track = track.append(sound.normalize(), crossfade=15)

        track_file = os.path.join(outdir, 'track_{0}.mp3'.format(i))
        track.export(track_file, format='mp3')
        tracks.append(track)

        # Tracklist info
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
