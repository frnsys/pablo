import config
from spotipy import Spotify, util
try:
    # python 3 only
    import stagger
    def get_artist_and_title(path):
        try:
            tags = stagger.read_tag(path)
        except stagger.NoTagError:
            return None, None
        return tags.artist, tags.title
except:
    import eyed3
    def get_artist_and_title(path):
        song = eyed3.load(path)
        return song.tag.artist, song.tag.title

TRACKS_CHUNK_SIZE = 50 # spotify API maximum

token = util.prompt_for_user_token(config.USERNAME,
                                   client_id=config.CLIENT_ID,
                                   client_secret=config.CLIENT_SECRET,
                                   redirect_uri=config.REDIRECT_URI)
spotify = Spotify(auth=token)


def get_spotify_track(path):
    artist, title = get_artist_and_title(path)
    if not artist or not title:
        return None
    query = 'artist:{} track:{}'.format(artist, title)
    resp = spotify.search(q=query, type='track')
    tracks = resp['tracks']['items']
    if len(tracks) == 0:
        return None
    else:
        return tracks[0]


def get_audio_features(paths):
    """
    gets audio features from the spotify API.
    refer to: <https://developer.spotify.com/web-api/get-several-audio-features/>
    interesting features:
        - acousticness
        - danceability
        - energy
        - instrumentalness
        - key
        - liveness
        - loudness
        - speechiness
        - mode
        - tempo
        - time_signature
        - valence
    """
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