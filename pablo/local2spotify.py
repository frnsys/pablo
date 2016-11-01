import config
import stagger
from spotipy import Spotify, util

TRACKS_CHUNK_SIZE = 50 # spotify API maximum

token = util.prompt_for_user_token(config.USERNAME,
                                   client_id=config.CLIENT_ID,
                                   client_secret=config.CLIENT_SECRET,
                                   redirect_uri=config.REDIRECT_URI)
spotify = Spotify(auth=token)


def get_spotify_track(path):
    try:
        tags = stagger.read_tag(path)
    except stagger.NoTagError:
        return None
    if not tags.artist or not tags.title:
        return None
    query = 'artist:{} track:{}'.format(tags.artist, tags.title)
    resp = spotify.search(q=query, type='track')
    tracks = resp['tracks']['items']
    if len(tracks) == 0:
        return None
    else:
        return tracks[0]


def get_audio_features(paths):
    tracks = [get_spotify_track(path) for path in paths]
    uris = [t['uri'] if t else None for t in tracks]
    valid_uris = [uri for uri in uris if uri is not None]
    results = {}
    for i in range(0, len(valid_uris), TRACKS_CHUNK_SIZE):
        for result in spotify.audio_features(tracks=valid_uris[i:i+TRACKS_CHUNK_SIZE]):
            results[result['uri']] = result
    return [{
        'features': results[track['uri']],
        'meta': track} if track else None for track in tracks]