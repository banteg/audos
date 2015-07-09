from scipy.io.wavfile import read, write
from numpy.fft import rfft, irfft
from subprocess import call
import numpy as np
import sys
import os

'''
Audos Sync
Sync HQ sound to recorded sound in video.

Usage:
python audos.py [video] [music]

It is presumed that video has mono sound and audio has stereo sound
'''


def silence(samples):
    return np.zeros((samples, 2), dtype=np.int16) # dtype=data.dtype


def extract_wav(in_name, out_name):
    print('extract wav: {}'.format(in_name))
    cmd = 'ffmpeg -y -i "{}" -ac 1 -ar 44100 "{}"'.format(in_name, out_name)
    call(cmd)


def mux(video, audio):
    print('mux to superfile')
    cmd = 'ffmpeg -y -i "{}" -i "{}" -c copy -map 0:0 -map 1 audos_render.mp4'.format(video, audio)
    call(cmd)


def autocorrelation(signal_a, signal_b, samples):
    print('compute autocorrelation')
    x = signal_a[:samples]
    y = signal_b[:samples]

    x = rfft(x)
    y = rfft(y[::-1])

    cc = irfft(x * y)
    cci = [(v, i) for i, v in enumerate(cc)]
    result = max(cci)[1]

    return result


def sync(data, samples, length):

    if samples < 0:
        # cut off data
        data = data[samples:]
    else:
        # pad left with silence
        print('pad left', samples)
        lpad = silence(samples)
        data = np.vstack([lpad, data])

    rdif = length - len(data)
    if rdif > 0:
        # pad right with silence
        print('pad right', rdif)
        rpad = silence(rdif)
        data = np.vstack([data, rpad])
    else:
        # cut right to fit
        print('cut right')
        data = data[:length]

    write('tmp_audio_hq_sync.wav', 44100, data)


def main():
    print('Audos is performing magic.')
    _, video, audio = sys.argv

    extract_wav(video, 'tmp_video.wav')
    extract_wav(audio, 'tmp_audio.wav')
    call('ffmpeg -y -i "{}" -ar 44100 tmp_audio_hq.wav'.format(audio))

    _, vdata = read('tmp_video.wav')
    _, adata = read('tmp_audio.wav')
    _, hqdata = read('tmp_audio_hq.wav')

    adjust = autocorrelation(vdata, adata, 44100 * 10)
    sync(hqdata, adjust, len(vdata))

    call('qaac -v256 --no-delay tmp_audio_hq_sync.wav')
    mux(video, 'tmp_audio_hq_sync.m4a')


if __name__ == '__main__':
    main()
