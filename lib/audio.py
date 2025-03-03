import re
import os

from mutagen.oggvorbis import OggVorbis
import tqdm


def get_audio_markers(path: str):
    markers = []
    for tag, value in OggVorbis(path).tags:
        if value.startswith('00:'):
            ts = re.search(r'00:00:0?(\d{1,2}\.\d{2})', value).groups()[0]
            markers.append(f"S+{ts}")
    return markers


def add_audio_volume(path: str, save_path: str = None, db: float = 1.0):
    # works only with Python <= 3.12
    from pydub import AudioSegment
    audio = AudioSegment.from_file(path, format="ogg")
    louder_audio = audio + db
    louder_audio.export(save_path or path, format="ogg")


def add_audio_folder_volume(directory, db: float = 1.0):
    for filename in tqdm.tqdm(os.listdir(directory)):
        add_audio_volume(os.path.join(directory, filename), db=db)
