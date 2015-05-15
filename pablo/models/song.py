from pablo.models.sample import Sample
from pablo.heuristics import assemble_samples


class Song():
    """
    A song and its constituent samples.
    """
    def __init__(self, name, slices, chunk_sizes):
        """
        The smallest chunk size should be the slice size.
        """
        self.name = name
        self.slices = slices
        self.sizes = chunk_sizes

        # Assemble the samples, starting with the smallest
        self.min_size = min(self.sizes)
        self.samples = {
            self.min_size: [Sample((s,), self, self.min_size, i) if s is not None else None
                       for i, s in enumerate(self.slices)]
        }

        # Create samples of larger chunk sizes.
        for size, size_ in zip(self.sizes, self.sizes[1:]):
            self.samples[size_] = assemble_samples(self.samples[size])


    def __getitem__(self, size):
        """
        Samples for the given size
        """
        return self.samples[size]


    def next_sample(self, prev_sample, size):
        """
        Returns the next sample of a given size, after the
        specified sample (which can be of any size).
        Returns None if it is a gap or the end of the song is reached.
        """
        nidx = (prev_sample.size/size * prev_sample.index) + 1
        if len(self[size]) <= nidx:
            return None
        else:
            return self[size][nidx]
