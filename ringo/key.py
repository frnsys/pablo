class Key():
    maj_keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    min_keys = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
    mixables = ['C', 'F', 'A#', 'D#', 'G#', 'C#', 'F#', 'B', 'E', 'A', 'D', 'G']
    n_notes  = 12

    def __init__(self, key, scale):
        if scale == 'major':
            self.idx = self.maj_keys.index(key)
        else:
            self.idx = self.min_keys.index(key)
        self.key = key
        self.scale = scale


    def distance(self, to_key):
        """
        Returns the shortest semitone distance from this key
        to the specified key.
        """
        return self._shortest_distance(self.idx, to_key.idx)


    def mixable(self, target_key):
        """
        Returns whether or not this key is "mixable" with
        the target key, as defined by the Camelot mixing wheel:
        <http://www.mixedinkey.com/HowTo>
        """
        # If they are the same key
        # or relative keys, they are mixable
        if self.idx == target_key.idx:
            return True

        # If they are the same scale and w/in
        # one key of each other, they are mixable
        if self.scale == target_key.scale:
            i = self.mixables.index(self.key)
            j = self.mixables.index(target_key.key)
            return abs(self._shortest_distance(i, j)) == 1

        return False


    def _shortest_distance(self, i, j):
        dist = j - i
        if abs(dist) > self.n_notes//2:
            dist = dist - self.n_notes if dist > 0 else dist + self.n_notes

        return dist
