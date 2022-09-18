from crowdin_api import CrowdinClient
from settings.crowdin import *
from collections import Counter
from datetime import datetime, timedelta
from typing import Callable, List, Dict

import pytz

utc = pytz.UTC


class Crowdin:
    def __init__(self):
        class Client(CrowdinClient):
            TOKEN = TOKEN

        self.client = Client()

    def get_all_translations(self, project_id: int):
        res = []
        offset = 0
        while True:
            data = self.client.string_translations.list_language_translations(
                project_id, 'uk', limit=500, offset=offset)['data']
            if not data:
                break
            offset += 500
            for t in data:
                t = t['data']
                res.append({'id': t['user']['id'], 'createdAt': t['createdAt'].replace(tzinfo=utc)})
        return res

    def get_project_files(self, project_id):
        return [f['data']['id'] for f in self.client.source_files.list_files(project_id, limit=500)['data']]

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

    @staticmethod
    def _get_users_counter_last_week(project_id: int, func: Callable) -> Counter:
        ts = (datetime.now() - timedelta(days=7)).replace(tzinfo=utc)
        users = Counter()
        res = func(project_id)
        for i in res:
            if i['createdAt'] > ts:
                users[i['id']] += 1
        return users

    def get_translators_last_week(self, project_id: int) -> Counter:
        return self._get_users_counter_last_week(project_id, self.get_all_translations)

    def get_commenters_last_week(self, project_id: int) -> Counter:
        return self._get_users_counter_last_week(project_id, self.get_all_comments)

    def get_approvers_last_week(self, project_id: int) -> Counter:
        return self._get_users_counter_last_week(project_id, self.get_all_approves)

    @staticmethod
    def _get_total_by_projects(list_projects: List[int], func: Callable) -> Counter:
        res = Counter()
        for jid in list_projects:
            res += func(jid)
        return res

    def get_total_translators(self, list_projects: List[int]) -> Counter:
        return self._get_total_by_projects(list_projects, self.get_translators_last_week)

    def get_total_approvers(self, list_projects: List[int]) -> Counter:
        return self._get_total_by_projects(list_projects, self.get_approvers_last_week)

    def get_total_commenters(self, list_projects: List[int]) -> Counter:
        return self._get_total_by_projects(list_projects, self.get_commenters_last_week)

    def get_top_contributors_last_week(self, list_projects: List[int]) -> Counter:
        return (
                self.get_total_translators(list_projects) +
                self.get_total_approvers(list_projects) +
                self.get_total_commenters(list_projects)
        )

    def get_users_usernames(self, users: List[int], list_projects: List[int]) -> dict:
        usernames = {}
        for uid in users:
            for jid in list_projects:
                try:
                    u = self.client.users.get_member_info(jid, uid)
                except:
                    continue
                usernames[uid] = u['data'].get('username') or u['data'].get('fullName')
                break
        return usernames

    def get_top_contributors_usernames(self, list_projects: List[int] = PROJECT_LIST) -> Dict[str, int]:
        users = self.get_top_contributors_last_week(list_projects)
        usernames = self.get_users_usernames(list(users), list_projects)
        return {usernames[u]: cnt for u, cnt in users.most_common()}
