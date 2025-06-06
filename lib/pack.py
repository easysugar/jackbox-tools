import os
import zipfile
from datetime import datetime

import tqdm

from lib.common import copy_file
from lib.game import update_localization

skip_words = ['copy', 'копія']


def _copy_to_release(src: str, dst: str, start_ts: datetime):
    print('Coping to release')
    for root, dirs, files in tqdm.tqdm(list(os.walk(src, topdown=False))):
        for f in files:
            fpath = os.path.join(root, f)
            if any(skip_word in fpath for skip_word in skip_words):
                continue
            ts = datetime.fromtimestamp(os.path.getmtime(fpath))
            if ts >= start_ts:  # or abs(os.path.getctime(fpath) - os.path.getmtime(fpath)) > 600:
                # or ts <= start_ts - timedelta(days=1) or (os.path.getmtime(fpath) - os.path.getctime(fpath) > 60):
                copy_file(fpath, fpath.replace(src, dst))


def _make_archive(src: str, archive_name: str = 'release.zip'):
    zip_path = os.path.join(src, '.releases', archive_name)
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)
    zip_process = zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED)
    for folder_path, _, filenames in tqdm.tqdm(os.walk(src)):
        if any([f.startswith('.') for f in folder_path.split(os.sep)]):
            continue
        for filename in filenames:
            filepath = os.path.join(src, folder_path, filename)
            if not filename.startswith('.'):
                zip_process.write(filepath, os.path.relpath(filepath, src))
    zip_process.close()
    print("Created archive")


class GamePack:
    games = []
    path_game = ''
    path_release = ''
    install_date = None
    release_name = ''
    localizations = {}  # build path -> array of source paths

    def decode_all(self):
        for game in self.games:
            game.decode_all()
        for src, *dst in self.localizations.items():
            for localization_file in dst:
                update_localization(os.path.join(self.path_game, localization_file), src)

    def copy_to_release(self):
        _copy_to_release(self.path_game, self.path_release, self.install_date)

    def make_release(self):
        _make_archive(self.path_release, self.release_name)
