import os

import tqdm
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from lib.game import read_json
from settings.drive import *


class Drive:
    def __init__(self):
        self.gauth = GoogleAuth()
        self.drive = GoogleDrive(self.gauth)

    def copy_audio_files_to_drive(self, game: str, path_subtitles: str, path_audio_folder: str):
        subtitles = read_json(path_subtitles)
        ids = list(subtitles)
        for _id in tqdm.tqdm(ids):
            file = os.path.join(path_audio_folder, f'{_id}.ogg')
            gfile = self.drive.CreateFile({'parents': [{'id': FOLDERS[game]}], 'title': f'{_id}.ogg'})
            # Read file and set it as the content of this instance.
            gfile.SetContentFile(file)
            gfile.Upload()  # Upload the file.
