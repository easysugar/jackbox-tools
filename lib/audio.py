import re

from mutagen.oggvorbis import OggVorbis


def get_audio_markers(path: str):
    markers = []
    for tag, value in OggVorbis(path).tags:
        if value.startswith('00:'):
            ts = re.search(r'00:00:0?(\d{1,2}\.\d{2})', value).groups()[0]
            markers.append(f"S+{ts}")
    return markers
