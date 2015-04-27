#! /usr/bin/env python3

from time import sleep
from os import path
import re


_THRESHOLD = 20
_LIGHT_SENSOR = '/sys/devices/platform/applesmc.768/light'
_KBD_BACKLIGHT = '/sys/class/leds/smc::kbd_backlight'
_SCREEN_BACKLIGHT = '/sys/class/backlight/gmux_backlight'

_FMT = re.compile(r'^\((\d+),(\d+)\)$')

_POLL_INTERVAL = 5


def _getlimits(basedir):
    with open(path.join(basedir, 'max_brightness')) as fp:
        return int(fp.read().strip())


LIMITS = {'screen': _getlimits(_SCREEN_BACKLIGHT),
          'keyboard': _getlimits(_KBD_BACKLIGHT)}


def bl(device, brightness=None):
    with open(path.join({'screen': _SCREEN_BACKLIGHT,
                         'keyboard': _KBD_BACKLIGHT}[device],
                        'brightness'), 'r+') as fp:
        if brightness is None:
            return int(fp.read().strip())
        else:
            brightness = int(brightness)
            assert brightness <= LIMITS[device], (brightness, LIMITS[device])
            print(brightness, file=fp)


def bangbang(args):
    if left < args.threshold:
        bl('keyboard', LIMITS['keyboard'])
        bl('screen', args.minimum_brightness)
    else:
        bl('keyboard', 0)
        bl('screen', LIMITS['screen'])


def proportional(args):
    if left < args.threshold:
        bl('keyboard', LIMITS['keyboard'] * (1 - left/_THRESHOLD))
        bl('screen', args.minimum_brightness +
                     LIMITS['screen'] * (left/_THRESHOLD))
    else:
        bl('keyboard', 0)
        bl('screen', LIMITS['screen'])


def inverse(args):
    if left < args.threshold:
        bl('keyboard', LIMITS['keyboard'] * left/_THRESHOLD)
        bl('screen', args.minimum_brightness +
                     LIMITS['screen'] * (left/_THRESHOLD))
    else:
        bl('keyboard', 0)
        bl('screen', LIMITS['screen'])


_GOVERNORS = {'bangbang': bangbang,
              'proportional': proportional,
              'inverse': inverse}


if __name__ == '__main__':
    from argparse import ArgumentParser

    ap = ArgumentParser(description='Macbook automatic backlight daemon')
    ap.add_argument('-t', '--threshold',
                    type=int, default=_THRESHOLD,
                    help='Threshold value for light sensor to turn '
                         'on keyboard backlight')
    ap.add_argument('-n', '--poll-interval',
                    type=int, default=_POLL_INTERVAL,
                    help='Time between light level reads')
    ap.add_argument('-g', '--governor',
                    default='bangbang', choices=_GOVERNORS, nargs='?',
                    help='Brightness regulation governor')
    ap.add_argument('-b', '--minimum-brightness',
                    type=int, default=LIMITS['screen'] // 2,
                    help='Minimum screen brightness')
    args = ap.parse_args()

    with open(_LIGHT_SENSOR) as fp:
        while True:
            left, right = map(int, _FMT.match(fp.read()).groups())

            _GOVERNORS[args.governor](args)

            fp.seek(0)
            sleep(args.poll_interval)
