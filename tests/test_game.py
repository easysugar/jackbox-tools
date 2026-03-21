import unittest

from lib.game import Game


class TestGame(unittest.TestCase):
    def test_get_context(self):
        g = Game()
        # empty content
        self.assertEqual(g.get_context({}), '')
        self.assertEqual(g.get_context({}, 'A'), 'A')
        self.assertEqual(g.get_context({}, 'A', 'B', ), 'A\nB')
        # 18+ mark
        self.assertEqual(g.get_context({'x': True}), '18+')
        self.assertEqual(g.get_context({'x': True}, 'A'), 'A\n-------------18+')
        self.assertEqual(g.get_context({'x': True}, 'A', 'B'), 'A\nB\n-------------18+')
        # USA mark
        self.assertEqual(g.get_context({'us': True}), 'for USA')
        self.assertEqual(g.get_context({'us': True}, 'A'), 'A\n-------------for USA')
        self.assertEqual(g.get_context({'us': True}, 'A', 'B'), 'A\nB\n-------------for USA')
        # 18+ and USA marks together
        self.assertEqual(g.get_context({'x': True, 'us': True}), 'for USA\n18+')
        self.assertEqual(g.get_context({'x': True, 'us': True}, 'A'), 'A\n-------------for USA\n18+')
        self.assertEqual(g.get_context({'x': True, 'us': True}, 'A', 'B'), 'A\nB\n-------------for USA\n18+')
        # with empty values in extra
        self.assertEqual(g.get_context({}, ''), '')
        self.assertEqual(g.get_context({}, 'A', '', None, 'B', ''), 'A\nB')
        self.assertEqual(g.get_context({'x': True}, '', 'A', ''), 'A\n-------------18+')
