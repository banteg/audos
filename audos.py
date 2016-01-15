import os
import warnings
from glob import glob
from subprocess import call

import click
import numpy as np
from numpy.fft import rfft, irfft
from scipy.io.wavfile import read, write


FFMPEG_EXTRACT_WAV = 'ffmpeg -loglevel panic -y -i "{i}" -ar {ar} "{o}"'
FFMPEG_MUX = 'ffmpeg -loglevel panic -y -i "{i[0]}" -i "{i[1]}" -c copy -map 0:0 -map 1 "{o}"'
QAAC_ENCODE = 'qaac -s -v256 --no-delay {i}'


def estimate_delay(a, b, rate, window=np.infty):
    if len(a.shape) > 1:
        a = np.mean(a, axis=1)
    if len(b.shape) > 1:
        b = np.mean(b, axis=1)

    samples = min(len(a), len(b), window * rate)

    a = a[:samples]
    b = b[:samples]

    xcorr = irfft(rfft(a) * rfft(b[::-1]))
    delay = np.argmax(xcorr)

    if delay > samples / 2:
        return delay - samples

    return delay


def silence(samples):
    return np.zeros((samples, 2), dtype=np.int16)


def sync(data, adjust, rate, length):
    if adjust < 0:
        # cut left
        data = data[-adjust:]
    else:
        # pad left
        lpad = silence(adjust)
        data = np.vstack([lpad, data])

    rdif = length - len(data)

    if rdif < 0:
        # cut right
        data = data[:length]
    else:
        # pad right
        rpad = silence(rdif)
        data = np.vstack([data, rpad])

    write('tmp_sync.wav', rate, data)


def cleanup():
    for i in glob('tmp_*'):
        os.unlink(i)


@click.command()
@click.argument('video', type=click.Path(exists=True, dir_okay=False))
@click.argument('audio', type=click.Path(exists=True, dir_okay=False))
@click.option('rate', '-r', '--rate', default=44100, help='Sample rate (samples/second)')
@click.option('window', '-w', '--window', default=30, help='Search window (seconds)')
@click.option('calc', '-c', '--calc', is_flag=True, help='Calculate only')
def main(video, audio, rate, window, calc):
    warnings.filterwarnings("ignore")

    click.secho('Audos is performing magic.', fg='yellow')
    click.echo('video={}  audio={}  rate={}  window={}\n'.format(video, audio, rate, window))

    click.echo('Extracting waveform from video')
    call(FFMPEG_EXTRACT_WAV.format(i=video, ar=rate, o='tmp_video.wav'))

    click.echo('Extracting waveform from audio\n')
    call(FFMPEG_EXTRACT_WAV.format(i=audio, ar=rate, o='tmp_audio.wav'))

    click.echo('Loading video waveform')
    sr, video_wave = read('tmp_video.wav')

    click.echo('Loading audio waveform\n')
    sr, audio_wave = read('tmp_audio.wav')

    click.echo('Estimating sync')
    adjust = estimate_delay(video_wave, audio_wave, window, rate)

    if calc:
        click.secho('Offset {:0.5f}s ({} frames)\n'.format(adjust / rate, adjust), fg='green')
        cleanup()
        return

    click.secho('Adjusting {:0.5f}s ({} frames)\n'.format(adjust / rate, adjust), fg='green')
    sync(audio_wave, adjust, rate, len(video_wave))

    click.echo('Encoding audio')
    call(QAAC_ENCODE.format(i='tmp_sync.wav'))

    click.echo('Muxing it all together')
    name = '{name}-audos.mp4'.format(name=os.path.splitext(video)[0])
    call(FFMPEG_MUX.format(i=[video, 'tmp_sync.m4a'], o=name))

    cleanup()

    click.secho('Saved as {name}'.format(name=name), fg='green')


if __name__ == '__main__':
    main()
