import unittest
from unittest.mock import mock_open, patch

from lib.common import copy_file, read_json, write_json


class TestCommon(unittest.TestCase):
    @patch('lib.common.shutil.copyfile')
    @patch('lib.common.Path.mkdir')
    def test_copy_file_creates_parent_directories(self, mkdir_mock, copyfile_mock):
        copy_file('src/file.txt', 'dst/nested/file.txt')

        mkdir_mock.assert_called_once_with(parents=True, exist_ok=True)
        copyfile_mock.assert_called_once_with('src/file.txt', 'dst/nested/file.txt')

    @patch('builtins.open', new_callable=mock_open, read_data='\ufeff{"value": 1}'.encode('utf-8'))
    def test_read_json_supports_utf8_bom(self, open_mock):
        self.assertEqual(read_json('bom.json'), {'value': 1})
        open_mock.assert_called_once_with('bom.json', 'rb')

    @patch('lib.common.json.dump')
    @patch('lib.common.os.makedirs')
    def test_write_json_creates_parent_directories_and_preserves_unicode(self, makedirs_mock, json_dump_mock):
        with patch('builtins.open', mock_open()) as open_mock:
            payload = {'text': 'Привіт'}

            write_json('deep/data.json', payload)

        makedirs_mock.assert_called_once_with('deep', exist_ok=True)
        open_mock.assert_called_once_with('deep/data.json', 'w', encoding='utf8', newline='\n')
        json_dump_mock.assert_called_once()
        self.assertEqual(json_dump_mock.call_args.args[0], payload)
