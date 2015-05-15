class Sample():
    """
    A sample for a song, composed of slices (parts).
    """
    def __init__(self, slices, song, size, index):
        self.slices = slices
        self.song = song
        self.size = size
        self.index = index


class Slice():
    """
    A sample of the smallest size, used to construct
    longer samples.
    """
    def __init__(self, file, song):
        self.song = song
        self.file = file


