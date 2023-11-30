import os
from typing import Dict

import tqdm
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from lib.game import read_json
from settings.drive import *


class Drive:
    def __init__(self, path_drive: str = None):
        self.gauth = GoogleAuth()
        self.gauth.LocalWebserverAuth()
        self.drive = GoogleDrive(self.gauth)
        self.path_drive = path_drive
        self.uploaded = self.get_uploaded_files(self.path_drive) if self.path_drive else set()
        self.links = None

    def upload(self, *path, name=None):
        name = path[-1] if not name else name
        if name not in self.uploaded:
            self.copy_to_drive(self.path_drive, os.path.join(*path), name)
            self.uploaded.add(name)

    def copy_to_drive(self, folder, filepath, filename):
        gfile = self.drive.CreateFile({'parents': [{'id': folder}], 'title': filename})
        gfile.SetContentFile(filepath)
        gfile.Upload()

    def copy_audio_subtitles_to_drive(self, game: str):
        self.upload_audio_to_drive(SUBTITLES[game], MEDIA_FOLDER[game], DRIVE_FOLDER[game])

    def upload_audio_to_drive(self, path: str, path_media: str, path_drive: str):
        subtitles = read_json(path)
        ids = list(subtitles)
        for _id in tqdm.tqdm(ids):
            file = os.path.join(path_media, f'{_id}.ogg')
            self.copy_to_drive(path_drive, file, f'{_id}.ogg')

    def copy_audio_to_drive_by_walk(self, game: str, src: str):
        for root, _, files in tqdm.tqdm(list(os.walk(src))):
            files = [f for f in files if f.endswith('.ogg')]
            assert len(files) <= 1
            folder = root.split(os.path.sep)[-1]
            for name in files:
                filepath = os.path.join(root, name)
                self.copy_to_drive(DRIVE_FOLDER[game], filepath, f'{folder}.ogg')

    def get_uploaded_files(self, path_drive):
        file_list = self.drive.ListFile({'q': "'{}' in parents and trashed=false".format(path_drive)}).GetList()
        return {file['originalFilename'] for file in file_list}

    def get_files_links(self, game: str = None, path_drive: str = None) -> Dict[str, str]:
        path_drive = path_drive or DRIVE_FOLDER[game]
        file_list = self.drive.ListFile({'q': "'{}' in parents and trashed=false".format(path_drive)}).GetList()
        return {file['originalFilename'].split('.')[0]: file['alternateLink'] for file in file_list}

    def get_link(self, _id: str):
        if self.links is None:
            self.links = self.get_files_links(path_drive=self.path_drive)
        return self.links[_id.removesuffix('.ogg')]
