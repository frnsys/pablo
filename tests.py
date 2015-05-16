from pablo import heuristics
from pablo.models.key import Key
from pablo.models.song import Song
from pablo.models.sample import Slice
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
    #def test_assemble_samples(self):
        #samples = [('a',), ('b',), None, ('c',), ('d',), ('e',)]
        #samples_ = heuristics.assemble_samples(samples)
        #self.assertEqual(samples_, [('a','b'), None, ('d', 'e')])

        #samples_ = heuristics.assemble_samples(samples_)
        #self.assertEqual(samples_, [None])


    def test_build_bar(self):
        for _ in range(20):
            names = ['Summer Crane', 'Frontier Psychiatrist', 'Electricity']
            sizes = [16, 32]
            songs = [self._song_factory(name, sizes=sizes) for name in names]

            length = 256
            track = heuristics.build_bar(songs, length)
            expected_n_slices = length/sizes[0]

            # Flatten the track into slices
            track = sum([s.slices for s in track], ())

            self.assertEqual(len(track), expected_n_slices)


    def _song_factory(self, name, sizes=[16, 32]):
        slices = [Slice('slice_{0}'.format(i)) for i in range(10)]
        song = Song(name, slices, sizes)
        return song
