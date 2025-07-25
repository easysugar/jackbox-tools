import json
import time
import zipfile
from collections import Counter
from datetime import datetime, timedelta
from typing import Callable, List, Dict, Set

import pytz
import requests
import tqdm
from crowdin_api import CrowdinClient

from settings.crowdin import *

utc = pytz.UTC


class Crowdin:
    def __init__(self, start_ts: datetime = None):
        class Client(CrowdinClient):
            TOKEN = TOKEN

        self.client = Client()
        self.start_ts = (start_ts or datetime.now() - timedelta(days=7)).replace(tzinfo=utc)
        self.usernames = {}

    def get_directory_id(self, project_id: int, directory_name: str) -> int:
        dirs = self.client.source_files.list_directories(project_id, filter=directory_name, recursion=True, limit=500)['data']
        return dirs[0]['data']['id']

    def get_all_translations(self, project_id: int, directory_id=None):
        res = []
        offset = 0
        while True:
            data = self.client.string_translations.list_language_translations('uk', project_id, directoryId=directory_id,
                                                                              limit=500, offset=offset)['data']
            if not data:
                break
            offset += 500
            for t in data:
                t = t['data']
                # if strings_ids is not None and t['stringId'] not in strings_ids:
                #     continue
                item = {
                    'id': t['user']['id'],
                    'username': t['user'].get('username') or t['user'].get('fullName'),
                    'createdAt': t['createdAt'].replace(tzinfo=utc),
                    'string_id': t['stringId'],
                }
                res.append(item)
                self.usernames[item['id']] = item['username']
        return res

    def get_project_files(self, project_id, path: str = None):
        list_files = self.client.source_files.list_files(project_id, limit=500)
        return [f['data']['id'] for f in list_files['data'] if not path or f['data']['path'].startswith(path)]

    def get_all_approves(self, project_id):
        files = self.get_project_files(project_id)
        res = []
        for file in files:
            offset = 0
            while True:
                data = self.client.string_translations.list_translation_approvals(
                    project_id, fileId=file, limit=500, offset=offset, languageId='uk')['data']
                if not data:
                    break
                offset += 500
                for t in data:
                    t = t['data']
                    res.append({'id': t['user']['id'], 'createdAt': t['createdAt'].replace(tzinfo=utc)})
        return res

    def get_all_comments(self, project_id):
        res = []
        offset = 0
        while True:
            data = self.client.string_comments.list_string_comments(project_id, limit=500, offset=offset)['data']
            if not data:
                break
            offset += 500
            for t in data:
                t = t['data']
                res.append({'id': int(t['user']['id']), 'createdAt': t['createdAt'].replace(tzinfo=utc),
                            'text': t['text']})
        return res

    def get_all_strings(self, project_id: int) -> List[dict]:
        res = []
        offset = 0
        while True:
            data = self.client.source_strings.list_strings(project_id, limit=500, offset=offset)['data']
            if not data:
                break
            offset += 500
            for t in data:
                t = t['data']
                res.append(t['id'])
        return res

    def _get_users_counter_last_time(self, project_id: int, func: Callable, *args, **kwargs) -> Counter:
        ts = self.start_ts
        users = Counter()
        res = func(project_id, *args, **kwargs)
        for i in res:
            if i['createdAt'] > ts:
                users[i['id']] += 1
        return users

    def get_translators_last_time(self, project_id: int, path: str) -> Counter:
        directory_id = self.get_directory_id(project_id, path)
        return self._get_users_counter_last_time(project_id, self.get_all_translations, directory_id)

    def get_commenters_last_time(self, project_id: int) -> Counter:
        return self._get_users_counter_last_time(project_id, self.get_all_comments)

    def get_approvers_last_time(self, project_id: int) -> Counter:
        return self._get_users_counter_last_time(project_id, self.get_all_approves)

    @staticmethod
    def _get_total_by_projects(list_projects: List[int], func: Callable, *args, **kwargs) -> Counter:
        res = Counter()
        for jid in list_projects:
            res += func(jid, *args, **kwargs)
        return res

    def get_total_translators(self, list_projects: List[int], path) -> Counter:
        return self._get_total_by_projects(list_projects, self.get_translators_last_time, path)

    def get_total_approvers(self, list_projects: List[int]) -> Counter:
        return self._get_total_by_projects(list_projects, self.get_approvers_last_time)

    def get_total_commenters(self, list_projects: List[int]) -> Counter:
        return self._get_total_by_projects(list_projects, self.get_commenters_last_time)

    def get_top_contributors_last_time(self, list_projects: List[int], path: str) -> Counter:
        return (
            self.get_total_translators(list_projects, path)
            # self.get_total_approvers(list_projects) +
            # self.get_total_commenters(list_projects)
        )

    def get_users_info(self, users: List[int], list_projects: List[int]) -> dict:
        info = {}
        for uid in users:
            for jid in list_projects:
                try:
                    u = self.client.users.get_member_info(jid, uid)
                except:
                    continue
                if u['data'].get('username') and u['data'].get('fullName'):
                    try:
                        name = '{0} "{2}" {1}'.format(*u['data'].get('fullName').split(' ', 1), u['data'].get('username'))
                    except IndexError:
                        name = '{0} "{1}"'.format(u['data'].get('fullName'), u['data'].get('username'))
                else:
                    name = u['data'].get('username') or u['data'].get('fullName')
                info[uid] = {
                    'name': name,
                    'avatar': u['data'].get('avatarUrl'),
                }
                break
        return info

    def get_top_contributors_usernames(self, list_projects: List[int] = PROJECT_LIST.values(), path: str = None) -> List[dict]:
        users = self.get_top_contributors_last_time(list_projects, path)
        info = self.get_users_info(list(users), list_projects)
        return [{'name': info.get(u, {}).get('name') or self.usernames.get(u), 'count': cnt, 'url': None if u not in info else info[u]['avatar'],
                 'username': self.usernames.get(u)}
                for u, cnt in users.most_common()]

    def get_top_members_report(self, date_from: datetime = None, date_to: datetime = None, list_projects: List[int] = PROJECT_LIST.values()):
        date_from = date_from or (datetime.today() - timedelta(days=7)).replace(day=1)
        date_to = date_to or datetime.today()
        members = []
        for project_id in tqdm.tqdm(list_projects):
            request = {'name': 'top-members', 'schema': {'unit': 'strings', 'languageId': 'uk', 'format': 'json',
                                                         'dateFrom': date_from.astimezone().replace(microsecond=0).isoformat(),
                                                         'dateTo': date_to.astimezone().replace(microsecond=0).isoformat()}}
            response = self.client.reports.generate_report(project_id, request)
            report_id = response['data']['identifier']
            time.sleep(2)
            response = self.client.reports.download_report(project_id, report_id)
            body = requests.get(response['data']['url'])
            members += json.loads(body.text)['data']
        counter = Counter()
        info = {}
        for m in members:
            if m['user']['username'] == 'widget_anonymous_user':
                continue
            counter[m['user']['id']] += m['translated']
            info[m['user']['id']] = m['user']
        return [{**info[uid], 'count': cnt} for uid, cnt in counter.most_common()]

    def _get_last_build_id(self, project_id: int) -> int:
        build = self.client.translations.list_project_builds(project_id)['data'][0]['data']
        assert build['status'] == 'finished'
        # assert build['createdAt'].timestamp() >= (datetime.now() - timedelta(minutes=5)).timestamp(), f'Build is not the last: {build}'
        return build['id']

    def _download_build(self, project_id: int, build_id, path_build: str):
        url = self.client.translations.download_project_translations(build_id, project_id)['data']['url']
        r = requests.get(url)
        with open(path_build, 'wb') as f:
            f.write(r.content)

    def download_last_build(self, project_id: int, path_build='build.zip'):
        self._download_build(project_id, self._get_last_build_id(project_id), path_build)

    def create_build(self, project_id: int):
        self.client.translations.build_crowdin_project_translation(project_id)

    @staticmethod
    def unzip_build(path_build: str = 'build.zip', path_folder: str = 'build'):
        with zipfile.ZipFile(path_build, 'r') as zip_ref:
            zip_ref.extractall(path_folder)

    def get_strings_ids_map(self, project_id: int, file_id: int = None, file_path: str = None) -> Dict[str, int]:
        if file_id is None:
            file_id = [f['data']['id'] for f in self.client.source_files.list_files(project_id)['data'] if f['data']['path'] == file_path][0]
        result = {}
        offset = 0
        while True:
            batch = self.client.source_strings.list_strings(project_id, file_id, limit=500, offset=offset)
            if not batch or not batch['data']:
                return result
            for s in batch['data']:
                _id = s['data']['identifier'].split('.')[-1]
                if _id in result:
                    raise Exception(f'{_id} duplicated!')
                result[_id] = s['data']['id']
            offset += 500

    def get_string_ids(self, project_id: int, file_id: int) -> Set[int]:
        result = set()
        offset = 0
        while True:
            batch = self.client.source_strings.list_strings(project_id, file_id, limit=500, offset=offset)
            if not batch or not batch['data']:
                return result
            for s in batch['data']:
                result.add(s['data']['id'])
            offset += 500

    def get_strings_ids_in_directory(self, project_id: int, directory_name: str) -> Set[int]:
        directory_id = self.get_directory_id(project_id, directory_name)
        files = self.client.source_files.list_files(project_id, directoryId=directory_id, limit=500)['data']
        string_ids = set()
        for f in files:
            string_ids |= self.get_string_ids(project_id, f['data']['id'])
        return string_ids

    def publish_audio_links(self, project_id: int, links: dict, crowdin_audio_path: str):
        list_files = self.client.source_files.list_files(project_id, limit=500)
        file_id = [f['data']['id'] for f in list_files['data'] if f['data']['path'] == crowdin_audio_path][0]
        strings = self.get_strings_ids_map(project_id, file_id)
        for audio_id in tqdm.tqdm(list(strings)):
            self.publish_comment(project_id, strings[audio_id], links[audio_id])

    def publish_comment(self, project_id: int, string_id: int, text: str, target_language_id='uk'):
        self.client.string_comments.requester.request(
            method="post",
            path=self.client.string_comments.get_string_comments_path(projectId=project_id),
            request_data={
                "text": text,
                "stringId": string_id,
                "targetLanguageId": target_language_id,
                "type": 'comment',
                "issueType": None,
            },
        )

    def get_strings_texts(self, project_id: int, string_ids: List[int]):
        return {x: self.client.source_strings.get_string(project_id, x)['data']['text'] for x in string_ids}

    def get_approved_translations(self, project_id: int, string_ids: List[int]):
        return {
            sid: self.client.string_translations.get_translation(project_id, translationId=x['data']['translationId'])['data']['text']
            for sid in string_ids
            for x in self.client.string_translations.list_translation_approvals(project_id, stringId=sid, languageId='uk')['data']
        }

    def get_directories_ids(self, project_id: int) -> Dict[str, int]:
        directories = self.client.source_files.list_directories(project_id, limit=500)
        paths = {}
        for d in directories['data']:
            d = d['data']
            dir_id = d['id']
            if d['directoryId'] is None:
                paths[dir_id] = '/' + d['name']
            else:
                paths[dir_id] = paths[d['directoryId']] + '/' + d['name']
        return {v: k for k, v in paths.items()}

    def get_directory_progress(self, project_id: int, directory_id: int):
        data = self.client.translation_status.get_directory_progress(project_id, directory_id)['data'][0]['data']
        return {'translated': data['translationProgress'], 'approved': data['approvalProgress']}
