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

    def copy_audio_files_to_drive(self, game: str):
        subtitles = read_json(SUBTITLES[game])
        ids = list(subtitles)
        for _id in tqdm.tqdm(ids):
            file = os.path.join(MEDIA_FOLDER[game], f'{_id}.ogg')
            gfile = self.drive.CreateFile({'parents': [{'id': DRIVE_FOLDER[game]}], 'title': f'{_id}.ogg'})
            gfile.SetContentFile(file)
            gfile.Upload()

    def get_files_links(self, game) -> Dict[str, str]:
        file_list = self.drive.ListFile({'q': "'{}' in parents and trashed=false".format(DRIVE_FOLDER[game])}).GetList()
        return {file['originalFilename'].split('.')[0]: file['alternateLink'] for file in file_list}
