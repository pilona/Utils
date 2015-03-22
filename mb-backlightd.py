#! /usr/bin/env python3

from collections import namedtuple
from time import sleep
from os import path
import re


_THRESHOLD = 20
_LIGHT_SENSOR = '/sys/devices/platform/applesmc.768/light'
_KBD_BACKLIGHT = '/sys/class/leds/smc::kbd_backlight'
_SCREEN_BACKLIGHT = '/sys/class/backlight/gmux_backlight'

_FMT = re.compile(r'^\((\d+),(\d+)\)$')

_POLL_INTERVAL = 5


class _Limits(namedtuple('_Limits', ['min', 'max'])):
    def __contains__(self, elem):
        return self.min <= elem <= self.max


def _getlimits(basedir):
    with open(path.join(basedir, 'max_brightness')) as fp:
        return _Limits(0, int(fp.read().strip()))


LIMITS = {'screen': _getlimits(_SCREEN_BACKLIGHT),
          'keyboard': _getlimits(_KBD_BACKLIGHT)}


def bl(device, brightness=None):
    with open(path.join({'screen': _SCREEN_BACKLIGHT,
                         'keyboard': _KBD_BACKLIGHT}[device],
                        'brightness'), 'r+') as fp:
        if brightness is None:
            return int(fp.read().strip())
        else:
            assert brightness in LIMITS[device]
            print(brightness, file=fp)


if __name__ == '__main__':
    from argparse import ArgumentParser

    ap = ArgumentParser()
    ap.add_argument('-t', '--threshold',
                    type=int, default=_THRESHOLD,
                    help='Threshold value for light sensor to turn '
                         'on keyboard backlight')
    ap.add_argument('-n', '--poll-interval',
                    type=int, default=_POLL_INTERVAL,
                    help='Time between light level reads')
    args = ap.parse_args()

    with open(_LIGHT_SENSOR) as fp:
        while True:
            left, right = map(int, _FMT.match(fp.read()).groups())

            if left < args.threshold:
                bl('keyboard', _LIMITS['keyboard'].max)
                bl('screen', _LIMITS['screen'].max // 2)
            else:
                bl('keyboard', _LIMITS['keyboard'].min)
                bl('screen', _LIMITS['screen'].max)

            fp.seek(0)
            sleep(args.poll_interval)
