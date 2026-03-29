import logging
import os
import zipfile
from datetime import datetime

import tqdm

from lib.common import copy_file
from lib.game import update_localization

MANUAL_EDIT_GRACE_SECONDS = 600
SKIP_WORDS = ['copy', 'копія']


def _copy_to_release(src: str, dst: str, start_ts: datetime):
    start_ts_unix = start_ts.timestamp()
    logging.debug('Coping to release')
    for root, dirs, files in tqdm.tqdm(list(os.walk(src, topdown=False))):
        for f in files:
            fpath = os.path.join(root, f)
            filename = os.path.basename(fpath).casefold()
            if any(skip_word.casefold() in filename for skip_word in SKIP_WORDS):
                continue

            src_mtime = os.path.getmtime(fpath)
            if src_mtime <= start_ts_unix:
                continue

            dst_path = os.path.join(dst, os.path.relpath(fpath, src))
            if os.path.exists(dst_path):
                dst_mtime = os.path.getmtime(dst_path)
                if src_mtime <= dst_mtime and os.path.getsize(fpath) == os.path.getsize(dst_path):
                    continue
            copy_file(fpath, dst_path)


def _make_archive(src: str, archive_name: str = 'release.zip', platform: str = None, beta=False):
    if platform:
        archive_name = '{0}-{2}.{1}'.format(*archive_name.rsplit('.', 1), platform)
    if beta:
        archive_name = '{0}-beta.{1}'.format(*archive_name.rsplit('.', 1))
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
    if platform:
        src_platform = os.path.join(src, f'.{platform}')
        for folder_path, _, filenames in tqdm.tqdm(os.walk(src_platform)):
            for filename in filenames:
                filepath = os.path.join(src_platform, folder_path, filename)
                zip_process.write(filepath, os.path.relpath(filepath, src_platform))
    zip_process.close()
    logging.debug("Created archive")


class GamePack:
    games = []
    path_game = ''
    path_release = ''
    install_date = None
    release_name = ''
    localizations = {}  # build path -> array of source paths

    def decode_all(self):
        for game in self.games:
            game().decode_all()
        for src, dst in self.localizations.items():
            for localization_file in dst:
                update_localization(os.path.join(self.path_game, localization_file), src)

    def copy_to_release(self):
        _copy_to_release(self.path_game, self.path_release, self.install_date)

    def make_release(self, platform: str = None, beta=False):
        _make_archive(self.path_release, self.release_name, platform, beta)
