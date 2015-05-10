from ringo.key import Key
import unittest

class KeyTest(unittest.TestCase):
    def setUp(self):
        self.key = Key('C', 'major')


    def test_distances(self):
        key = Key('D', 'major')
        dist = self.key.distance(key)
        self.assertEqual(dist, 2)

        dist = key.distance(self.key)
        self.assertEqual(dist, -2)

        key = Key('B', 'major')
        dist = self.key.distance(key)
        self.assertEqual(dist, -1)

        dist = key.distance(self.key)
        self.assertEqual(dist, 1)

        key = Key('C', 'minor')
        dist = self.key.distance(key)
        self.assertEqual(dist, 3)

        dist = key.distance(self.key)
        self.assertEqual(dist, -3)


    def test_mixable(self):
        key = Key('F', 'major')
        mix = self.key.mixable(key)
        self.assertTrue(mix)

        key = Key('G', 'major')
        mix = self.key.mixable(key)
        self.assertTrue(mix)

        key = Key('A', 'minor')
        mix = self.key.mixable(key)
        self.assertTrue(mix)

        key = Key('B', 'minor')
        mix = self.key.mixable(key)
        self.assertFalse(mix)

        key = Key('B', 'major')
        mix = self.key.mixable(key)
        self.assertFalse(mix)
