# audos

![waveform](https://cloud.githubusercontent.com/assets/4562643/8623417/27ec4eb4-2753-11e5-906a-61f1dca4145b.png)

Sync sound with its recording.

## Usage

```
audos <video> <audio> [-r 44100] [-w 30] [-c]
```

## Options

`-r` or `--rate` sample rate in samples/second

`-w` or `--window` search window in seconds

`-c` or `--calc` calculate offset only

## Installation

You'll need Python 3, numpy, scipy, ffmpeg and qaac. Should work on any platform.

```
pip install git+https://github.com/banteg/audos
```
