from scipy.io.wavfile import read, write
from numpy.fft import rfft, irfft
from subprocess import call
import numpy as np
import sys
from glob import glob
import os


SEARCH_WINDOW = 30  # seconds, twice the maximum delay/rush


def silence(samples):
    return np.zeros((samples, 2), dtype=np.int16)


def extract_wav(in_name, out_name, channels=1):
    print('extract wav: {}'.format(in_name))
    cmd = 'ffmpeg -loglevel panic -y -i "{}" -ac {} -ar 44100 "{}"'.format(in_name, channels, out_name)
    call(cmd)


def mux(video, audio, output):
    print('mux to superfile')
    cmd = 'ffmpeg -loglevel panic -y -i "{}" -i "{}" -c copy -map 0:0 -map 1 "{}"'.format(video, audio, output)
    call(cmd)


def estimate_delay(signal_a, signal_b, samples):
    print('compute cross-correlation')
    x = signal_a[:samples]
    y = signal_b[:samples]

    xcorr = irfft(rfft(x) * rfft(y[::-1]))
    delay = np.argmax(xcorr)

    if delay > samples / 2:
        return delay - samples
    return delay


def sync(data, samples, length):
    if samples < 0:
        print('cut left {:0.5f}s'.format(-samples / 44100))
        data = data[-samples:]
    else:
        print('pad left {:0.5f}s'.format(samples / 44100))
        lpad = silence(samples)
        data = np.vstack([lpad, data])

    rdif = length - len(data)
    if rdif > 0:
        print('pad right {:0.5f}s'.format(rdif / 44100))
        rpad = silence(rdif)
        data = np.vstack([data, rpad])
    else:
        print('cut right')
        data = data[:length]

    write('tmp_audio_hq_sync.wav', 44100, data)


def main():
    print('Audos/dev is performing magic.')
    _, video, audio = sys.argv

    extract_wav(video, 'tmp_video.wav')
    extract_wav(audio, 'tmp_audio.wav')
    extract_wav(audio, 'tmp_audio_hq.wav', 2)

    _, vdata = read('tmp_video.wav')
    _, adata = read('tmp_audio.wav')
    _, hqdata = read('tmp_audio_hq.wav')

    adjust = estimate_delay(vdata, adata, 44100 * SEARCH_WINDOW)

    print('adjust {:0.5f}s ({} frames)'.format(adjust / 44100, adjust))
    sync(hqdata, adjust, len(vdata))

    print('encoding aac')
    call('qaac -s -v256 --no-delay tmp_audio_hq_sync.wav')
    mux(video, 'tmp_audio_hq_sync.m4a', '{}_audos.mp4'.format(video))

    for i in glob('tmp_*'):
        os.unlink(i)


if __name__ == '__main__':
    main()
