# Pablo

(work in progress)

It doesn't seem like the new Avalanches album is coming out any time soon, but with _Pablo_ (so named for [_Pablo's Cruise_](https://www.youtube.com/watch?v=7Ry8M8M-ICg)) you can automatically generate [plunderphonic](https://en.wikipedia.org/wiki/Plunderphonics) song sketches (music collages/sample mixes) to fill that void.

Pablo will analyze a directory of audio files (mp3, wav, aif) and randomly select a song to build a mix around. It will then pick out other appropriate songs from that directory - tempo-stretching and pitch-shifting them as needed - to slice into samples, which Pablo then assembles into a multi-track mix.

The quality of the output depends a lot on your own taste in curating the library Pablo samples from. If you have a directory of songs that seem like they'll fit together, Pablo will do pretty well. If you have a bunch of random tracks, you might get something nice too.

These mix sketches are meant for high-scale automated ideation and _not_ a substitute for human editing ;)


## Setup

Clone the git repo, then from inside the repo:

    $ pip install .

Pablo relies on some other libraries for the heavy lifting, so install those:

    $ brew install sox ffmpeg

And you'll also need [Essentia](http://essentia.upf.edu/documentation/installing.html). [Installation instructions are here](http://essentia.upf.edu/documentation/installing.html).


## Usage

You can have Pablo analyze your library in one go, so that mix generation runs quicker. Pablo will persist song analyses based on file hashes so no redundant processing is necessary.

    $ pablo analyze /path/to/my/songs

Then you can start generating mixes:

    $ pablo mix /path/to/my/songs /path/to/output

Pablo will output the mix, a tracklist for the mix, the modified songs, and all of the sliced samples to the specified output directory.

There are a few options you can pass in, to learn about them, help is available:

    $ pablo mix --help

You can also "crate dig" YouTube videos with the `dig` ability:

    $ pablo dig https://www.youtube.com/watch?v=uS2nWLz-AbE /path/to/output


## To do

- could favor more "[danceable](http://essentia.upf.edu/documentation/reference/std_Danceability.html)" tracks as rhythm tracks


## Pie-in-the-sky

- use [Gaia](https://github.com/MTG/gaia/tree/master/src/bindings/pygaia/scripts/classification) to train an audio classifier? then use this to have some notion of what kind of song to aim for?
- Gaia has some kind of music similarity capabilities, I think. Could use that to further filter down selections based on similarity
- could seed some songs and then crawl related youtube videos for automatic sample discovery
