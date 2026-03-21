import unittest

from lib.game import Game


class TestGame(unittest.TestCase):
    def test_get_context(self):
        g = Game()
        self.assertEqual(g.get_context({}), '')
        self.assertEqual(g.get_context({}, 'A'), 'A')
        self.assertEqual(g.get_context({}, 'A', 'B', ), 'A\nB')
        self.assertEqual(g.get_context({'x': True}), '18+')
        self.assertEqual(g.get_context({'x': True}, 'A'), 'A\n-------------18+')
        self.assertEqual(g.get_context({'x': True}, 'A', 'B'), 'A\nB\n-------------18+')
        self.assertEqual(g.get_context({'us': True}), 'for USA')
        self.assertEqual(g.get_context({'us': True}, 'A'), 'A\n-------------for USA')
        self.assertEqual(g.get_context({'us': True}, 'A', 'B'), 'A\nB\n-------------for USA')
        self.assertEqual(g.get_context({'x': True, 'us': True}), 'for USA\n18+')
        self.assertEqual(g.get_context({'x': True, 'us': True}, 'A'), 'A\n-------------for USA\n18+')
        self.assertEqual(g.get_context({'x': True, 'us': True}, 'A', 'B'), 'A\nB\n-------------for USA\n18+')
