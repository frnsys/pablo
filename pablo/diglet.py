import os
import requests
from lxml.html import fromstring
from youtube_dl import YoutubeDL


base = 'https://www.youtube.com'


def dig(start, outdir, depth=2, max_duration=360):
    """
    Crawls YouTube for source material (as mp3s).

    Args:
        - start: the starting YouTube url
        - outdir: directory to save download tracks to
        - depth: how many levels of related vids to look through
        - max_duration: only dl videos shorter than or equal to this in duration
    """
    urls = [start]
    candidates = [start]

    # Dig
    while depth:
        candidates = sum((_get_related_video_urls(url) for url in candidates), [])
        urls += candidates
        depth -= 1

    # Remove dupes
    urls = set(urls)

    print('Got {0} videos'.format(len(urls)))

    # Kind of peculiar how this function has to work
    def _filter(info):
        if info['duration'] > max_duration:
            return 'Too long'
        return None

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'match_filter': _filter,
        'outtmpl': os.path.join(outdir, '%(title)s-%(id)s.%(ext)s'),
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download(urls)


def _get_related_video_urls(url, n=5):
    r = requests.get(url)
    html = fromstring(r.text)

    # Get the top 5 related videos
    results = []
    for el in html.cssselect('#watch-related .content-link')[:n]:
        results.append(base + el.get('href'))

    return results


if __name__ == '__main__':
    start = 'https://www.youtube.com/watch?v=uS2nWLz-AbE'
    dig(start, depth=2)