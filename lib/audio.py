import logging
import os
import re
from typing import List

import tqdm
from mutagen.oggvorbis import OggVorbis
from pydub import AudioSegment

logging.getLogger("pydub.converter").setLevel(logging.WARNING)


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


def gather_audio_files(audio_folder: str, audio_files: List[str], output_path: str, gap_duration_ms=1000):
    # Create a 1-second silence segment
    gap = AudioSegment.silent(duration=gap_duration_ms)

    # Initialize the combined audio
    combined = AudioSegment.empty()

    # Load and concatenate audio files with 1-second gaps
    logging.debug('Start audio gathering')
    for i, filename in enumerate(tqdm.tqdm(audio_files)):
        filepath = os.path.join(audio_folder, filename)
        audio = AudioSegment.from_file(filepath)
        if i > 0:
            combined += gap
        combined += audio

    combined.export(output_path, format="wav")
    logging.debug(f"Combined audio saved to {output_path}")
