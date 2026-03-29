import unittest
from unittest.mock import patch

from lib.game import (
    clean_text,
    normalize_text,
    read_from_folder,
    replace_suffix,
    replace_tags,
    update_localization,
    write_to_folder,
)


class TestGameUtils(unittest.TestCase):
    @patch('lib.game.read_json')
    def test_read_from_folder_returns_mapping_by_field_name(self, read_json_mock):
        read_json_mock.return_value = {
            'fields': [
                {'n': 'prompt', 'v': 'Hello'},
                {'n': 'answer', 'v': 'World'},
            ]
        }

        result = read_from_folder('42', 'content.jet')

        self.assertEqual(
            result,
            {
                'prompt': {'n': 'prompt', 'v': 'Hello'},
                'answer': {'n': 'answer', 'v': 'World'},
            },
        )
        read_json_mock.assert_called_once()

    @patch('lib.game.write_json')
    def test_write_to_folder_wraps_values_in_fields_payload(self, write_json_mock):
        value = {
            'prompt': {'n': 'prompt', 'v': 'Hello'},
            'answer': {'n': 'answer', 'v': 'World'},
        }

        write_to_folder('42', 'content.jet', value)

        write_json_mock.assert_called_once_with(
            'content\\42\\data.jet',
            {'fields': list(value.values())},
        )

    @patch('lib.game.write_json')
    @patch('lib.game.read_json')
    def test_update_localization_merges_translation_sources(self, read_json_mock, write_json_mock):
        read_json_mock.side_effect = [
            {'table': {'en': {'A': 'old a', 'B': 'old b'}}},
            {'table': {'en': {'A': 'new a'}}},
            {'B': 'new b'},
        ]

        update_localization('Localization.json', 'trans1.json', 'trans2.json')

        write_json_mock.assert_called_once_with(
            'Localization.json',
            {'table': {'en': {'A': 'new a', 'B': 'new b'}}},
        )

    def test_text_helpers_strip_tags_and_preserve_suffixes(self):
        self.assertEqual(clean_text(' [tag] Hello [/tag] '), 'Hello')
        self.assertEqual(normalize_text(' [TAG] HeLLo [/tag] '), 'hello')
        self.assertEqual(replace_suffix('Text [x]', 'Новий текст'), 'Новий текст[x]')
        self.assertEqual(replace_tags('[x] Text [y]', 'Нове значення'), '[x] Нове значення[y]')
