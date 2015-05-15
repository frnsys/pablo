from pablo.key import Key
from pablo import heuristics
import unittest

class KeyTests(unittest.TestCase):
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


class HeuristicsTests(unittest.TestCase):
    def test_build_bar(self):
        samples = {
            'Since I Left You': {
                8 : ['sily_08_01.mp3', 'sily_08_02.mp3'],
                16: ['sily_16_01.mp3', 'sily_16_02.mp3'],
                32: ['sily_32_01.mp3', 'sily_32_02.mp3'],
            },
            'Pablo\'s Cruise': {
                8 : ['pc_08_01.mp3', 'pc_08_02.mp3'],
                16: ['pc_16_01.mp3', 'pc_16_02.mp3'],
                32: ['pc_32_01.mp3', 'pc_32_02.mp3'],
            }
        }

        # eh need to make this an actual test
        bar = heuristics.build_bar(samples, 32)
        print(bar)


    def test_assemble_samples(self):
        samples = [('a',), ('b',), None, ('c',), ('d',), ('e',)]
        samples_ = heuristics.assemble_samples(samples)
        self.assertEqual(samples_, [('a','b'), None, ('d', 'e')])

        samples_ = heuristics.assemble_samples(samples_)
        self.assertEqual(samples_, [None])
