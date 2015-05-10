# Ringo

(work in progress)

It doesn't seem like the new Avalanches album is coming out any time soon, but with _Ringo_ you can automatically generate [plunderphonic](https://en.wikipedia.org/wiki/Plunderphonics) sketches to fill that void.

Ringo will analyze a directory of audio files (mp3, wav) and randomly select a song to build a mix around. It will then pick out other appropriate songs from that directory - tempo-stretching and pitch-shifting them as needed - to slice into samples, which Ringo then assembles into a multi-track mix.

Beat alignment is still kind of finicky, but the quality of the output depends a lot on your own taste in curating the library Ringo samples from. If you have a directory of songs that seem like they'll fit together, Ringo will do pretty well. If you have a bunch of random tracks, you might get something nice too.

These mix sketches are meant for high-scale automated ideation and _not_ a substitute for human editing ;)


## Usage

You can have Ringo analyze your library in one go, so that mix generation runs quicker. Ringo will persist song analyses based on file hashes so no redundant processing is necessary.

    $ python main.py analyze /path/to/my/songs

Then you can start generating mixes:

    $ python main.py mix /path/to/my/songs /path/to/output


## To do

- trim silence to better align beats?
- heuristics for aligning samples better (e.g. take max chunk size and box-fit into those chunk sizes)
- smoother transitions by crossfading? but without misaligning samples
- EQ heuristics? e.g. some samples are only low or mid or high
