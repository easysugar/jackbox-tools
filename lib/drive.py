import os
from typing import Dict

import tqdm
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from lib.game import read_json
from settings.drive import *


class Drive:
    def __init__(self):
        self.gauth = GoogleAuth()
        self.drive = GoogleDrive(self.gauth)

    def copy_to_drive(self, folder, filepath, filename):
        gfile = self.drive.CreateFile({'parents': [{'id': folder}], 'title': filename})
        gfile.SetContentFile(filepath)
        gfile.Upload()

    def copy_audio_subtitles_to_drive(self, game: str):
        subtitles = read_json(SUBTITLES[game])
        ids = list(subtitles)
        for _id in tqdm.tqdm(ids):
            file = os.path.join(MEDIA_FOLDER[game], f'{_id}.ogg')
            self.copy_to_drive(DRIVE_FOLDER[game], file, f'{_id}.ogg')

    def copy_audio_to_drive_by_walk(self, game: str, src: str):
        for root, _, files in tqdm.tqdm(list(os.walk(src))):
            files = [f for f in files if f.endswith('.ogg')]
            assert len(files) <= 1
            folder = root.split(os.path.sep)[-1]
            for name in files:
                filepath = os.path.join(root, name)
                self.copy_to_drive(DRIVE_FOLDER[game], filepath, f'{folder}.ogg')

    def get_files_links(self, game) -> Dict[str, str]:
        file_list = self.drive.ListFile({'q': "'{}' in parents and trashed=false".format(DRIVE_FOLDER[game])}).GetList()
        return {file['originalFilename'].split('.')[0]: file['alternateLink'] for file in file_list}
