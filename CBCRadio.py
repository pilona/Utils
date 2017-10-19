#! /usr/bin/env python3

'''
CBC Radio streams player/downloader
'''

from datetime import datetime
from argparse import ArgumentParser, OPTIONAL
from collections import namedtuple
import subprocess
import readline

import requests
from lxml import html

_STREAM_SNAPSHOT = [
    ("Radio One", "BC", "Kamloops",
     "http://cbc_r1_kam.akacast.akamaistream.net/7/440/451661/v1/rc.akacast.akamaistream.net/cbc_r1_kam"),
    ("Radio One", "BC", "Kelowna",
     "http://cbc_r1_kel.akacast.akamaistream.net/7/229/451661/v1/rc.akacast.akamaistream.net/cbc_r1_kel"),
    ("Radio One", "BC", "Prince George",
     "http://cbc_r1_prg.akacast.akamaistream.net/7/966/451661/v1/rc.akacast.akamaistream.net/cbc_r1_prg"),
    ("Radio One", "BC", "Vancouver",
     "http://cbc_r1_vcr.akacast.akamaistream.net/7/723/451661/v1/rc.akacast.akamaistream.net/cbc_r1_vcr"),
    ("Radio One", "BC", "Victoria",
     "http://cbc_r1_vic.akacast.akamaistream.net/7/728/451661/v1/rc.akacast.akamaistream.net/cbc_r1_vic"),
    ("Radio One", "Yukon", "Whitehorse",
     "http://cbc_r1_whs.akacast.akamaistream.net/7/319/451661/v1/rc.akacast.akamaistream.net/cbc_r1_whs"),
    ("Radio One", "Alberta", "Calgary",
     "http://cbc_r1_cgy.akacast.akamaistream.net/7/298/451661/v1/rc.akacast.akamaistream.net/cbc_r1_cgy"),
    ("Radio One", "Alberta", "Edmonton",
     "http://cbc_r1_edm.akacast.akamaistream.net/7/904/451661/v1/rc.akacast.akamaistream.net/cbc_r1_edm"),
    ("Radio One", "Saskatchewan", "Regina",
     "http://cbc_r1_reg.akacast.akamaistream.net/7/666/451661/v1/rc.akacast.akamaistream.net/cbc_r1_reg"),
    ("Radio One", "Saskatchewan", "Saskatoon",
     "http://cbc_r1_ssk.akacast.akamaistream.net/7/842/451661/v1/rc.akacast.akamaistream.net/cbc_r1_ssk"),
    ("Radio One", "Manitoba", "Winnipeg",
     "http://cbc_r1_wpg.akacast.akamaistream.net/7/831/451661/v1/rc.akacast.akamaistream.net/cbc_r1_wpg"),
    ("Radio One", "Nunavut", "Iqaluit",
     "http://cbc_r1_iqa.akacast.akamaistream.net/7/325/451661/v1/rc.akacast.akamaistream.net/cbc_r1_iqa"),
    ("Radio One", "Ontario", "Kitchener-Waterloo",
     "http://cbc_r1_ekw.akacast.akamaistream.net/7/63/451661/v1/rc.akacast.akamaistream.net/cbc_r1_ekw"),
    ("Radio One", "Ontario", "London",
     "http://cbc_r1_ldn.akacast.akamaistream.net/7/104/451661/v1/rc.akacast.akamaistream.net/cbc_r1_ldn"),
    ("Radio One", "Ontario", "Ottawa",
     "http://cbc_r1_ott.akacast.akamaistream.net/7/613/451661/v1/rc.akacast.akamaistream.net/cbc_r1_ott"),
    ("Radio One", "Ontario", "Sudbury",
     "http://cbc_r1_sud.akacast.akamaistream.net/7/380/451661/v1/rc.akacast.akamaistream.net/cbc_r1_sud"),
    ("Radio One", "Ontario", "Thunder Bay",
     "http://cbc_r1_tba.akacast.akamaistream.net/7/245/451661/v1/rc.akacast.akamaistream.net/cbc_r1_tba"),
    ("Radio One", "Ontario", "Toronto",
     "http://cbc_r1_tor.akacast.akamaistream.net/7/632/451661/v1/rc.akacast.akamaistream.net/cbc_r1_tor"),
    ("Radio One", "Ontario", "Windsor",
     "http://cbc_r1_wdr.akacast.akamaistream.net/7/813/451661/v1/rc.akacast.akamaistream.net/cbc_r1_wdr"),
    ("Radio One", "Quebec", "Montreal",
     "http://cbc_r1_mtl.akacast.akamaistream.net/7/35/451661/v1/rc.akacast.akamaistream.net/cbc_r1_mtl"),
    ("Radio One", "Quebec", "Nord Quebec",
     "http://cbc_r1_n_mtl.akacast.akamaistream.net/7/823/451661/v1/rc.akacast.akamaistream.net/cbc_r1_n_mtl"),
    ("Radio One", "Quebec", "Quebec City",
     "http://cbc_r1_qqu.akacast.akamaistream.net/7/29/451661/v1/rc.akacast.akamaistream.net/cbc_r1_qqu"),
    ("Radio One", "New Brunswick", "Fredericton",
     "http://cbc_r1_frd.akacast.akamaistream.net/7/553/451661/v1/rc.akacast.akamaistream.net/cbc_r1_frd"),
    ("Radio One", "New Brunswick", "Moncton",
     "http://cbc_r1_mct.akacast.akamaistream.net/7/383/451661/v1/rc.akacast.akamaistream.net/cbc_r1_mct"),
    ("Radio One", "New Brunswick", "Saint John",
     "http://cbc_r1_snb.akacast.akamaistream.net/7/754/451661/v1/rc.akacast.akamaistream.net/cbc_r1_snb"),
    ("Radio One", "Prince Edward Island", "Charlottetown",
     "http://cbc_r1_chr.akacast.akamaistream.net/7/169/451661/v1/rc.akacast.akamaistream.net/cbc_r1_chr"),
    ("Radio One", "Nova Scotia", "Cape Breton",
     "http://cbc_r1_syd.akacast.akamaistream.net/7/897/451661/v1/rc.akacast.akamaistream.net/cbc_r1_syd"),
    ("Radio One", "Nova Scotia", "Halifax",
     "http://cbc_r1_hfx.akacast.akamaistream.net/7/981/451661/v1/rc.akacast.akamaistream.net/cbc_r1_hfx"),
    ("Radio One", "Newfoundland & Labrador", "Corner Brook",
     "http://cbc_r2_cor.akacast.akamaistream.net/7/550/451661/v1/rc.akacast.akamaistream.net/cbc_r1_cor"),
    ("Radio One", "Newfoundland & Labrador", "Grand Falls/Gander",
     "http://cbc_r1_gfa.akacast.akamaistream.net/7/492/451661/v1/rc.akacast.akamaistream.net/cbc_r1_gfa"),
    ("Radio One", "Newfoundland & Labrador", "Labrador",
     "http://cbc_r1_gba.akacast.akamaistream.net/7/274/451661/v1/rc.akacast.akamaistream.net/cbc_r1_gba"),
    ("Radio One", "Newfoundland & Labrador", "St. John's",
     "http://cbc_r1_snf.akacast.akamaistream.net/7/750/451661/v1/rc.akacast.akamaistream.net/cbc_r1_snf"),
    ("Radio One", "Northwest Territories", "Inuvik",
     "http://cbc_r1_ink.akacast.akamaistream.net/7/967/451661/v1/rc.akacast.akamaistream.net/cbc_r1_ink"),
    ("Radio One", "Northwest Territories", "Yellowknife",
     "http://cbc_r1_ykn.akacast.akamaistream.net/7/369/451661/v1/rc.akacast.akamaistream.net/cbc_r1_ykn"),

    ("Radio Two", "Atlantic", "Halifax",
     "http://cbc_r2_hfx.akacast.akamaistream.net/7/917/451661/v1/rc.akacast.akamaistream.net/cbc_r2_hfx"),
    ("Radio Two", "Eastern", "Toronto",
     "http://cbc_r2_tor.akacast.akamaistream.net/7/364/451661/v1/rc.akacast.akamaistream.net/cbc_r2_tor"),
    ("Radio Two", "Central", "Winnipeg",
     "http://cbc_r2_wpg.akacast.akamaistream.net/7/233/451661/v1/rc.akacast.akamaistream.net/cbc_r2_wpg"),
    ("Radio Two", "Mountain", "Edmonton",
     "http://cbc_r2_edm.akacast.akamaistream.net/7/40/451661/v1/rc.akacast.akamaistream.net/cbc_r2_edm"),
    ("Radio Two", "Pacific", "Vancouver",
     "http://cbc_r2_vcr.akacast.akamaistream.net/7/773/451661/v1/rc.akacast.akamaistream.net/cbc_r2_vcr"),
    ("Radio Two", "International", "Pacific",
     "http://cbc_r2_ipt.akacast.akamaistream.net/7/669/451661/v1/rc.akacast.akamaistream.net/cbc_r2_ipt"),
    ("Radio Two", "International", "Eastern",
     "http://cbc_r2_iet.akacast.akamaistream.net/7/50/451661/v1/rc.akacast.akamaistream.net/cbc_r2_iet"),
]


# CBC Music stream list page
_STREAMS = 'http://www.cbc.ca/radio/includes/streams.html'
# CBC Radio 2 Eastern (Toronto) stream URL
CBC_RADIO_2 = 'http://cbc_r2_tor.akacast.akamaistream.net' \
              '/7/364/451661/v1/rc.akacast.akamaistream.net/cbc_r2_tor'
# CBC Radio 1 Ottawa stream URL
CBC_RADIO_1 = 'http://cbc_r1_ott.akacast.akamaistream.net' \
              '/7/613/451661/v1/rc.akacast.akamaistream.net/cbc_r1_ott'


argument_parser = ArgumentParser(__doc__)
argument_parser.add_argument('-l', '--list', action='store_true')
argument_parser.add_argument('-t', '--tee', action='store_true')
mutex_group = argument_parser.add_mutually_exclusive_group(required=False)
# Yuck, wish it was multiple arguments,
# but argparse doesn't support anything but OPTIONAL.
mutex_group.add_argument('stream', nargs=OPTIONAL, type=str.split,
                         help='Name of stream to play/record')
mutex_group.add_argument('-1', '--one', action='store_const', const=CBC_RADIO_1,
                         dest='url', help='CBC Radio One Eastern')
mutex_group.add_argument('-2', '--two', action='store_const', const=CBC_RADIO_2,
                         dest='url', help='CBC Radio Two Eastern')

PlaylistItem = namedtuple('PlaylistItem', ['radio', 'province', 'city', 'url'])

_COMPLETION_INDEX = {' '.join((radio, region, city)): url
                     for radio, region, city, url
                     in _STREAM_SNAPSHOT}


def get_streams():
    '''
    Get CBC Radio music streams as {name: stream_url}.
    '''
    r = requests.get(_STREAMS)
    r.raise_for_status()
    h = html.fromstring(r.content, base_url=r.url)  # noqa
    radio_one, radio_two = h.cssselect('table')
    for row in radio_one.cssselect('tbody td'):
        raise NotImplementedError()
    for row in radio_two.cssselect('tbody td'):
        raise NotImplementedError()


class Completer:
    def __init__(self, streams):
        self.streams = streams
        self.previous_prefix = None

    def complete(self, text, state):
        if text != self.previous_prefix:
            #print('!' * 200)
            self.completions = [stream
                                for stream
                                in self.streams
                                if readline.get_line_buffer().strip() in stream]
        self.previous_prefix = text
        try:
            return self.completions[state]
        except IndexError:
            return None


def mpv_cmdline(input_url):
    '''
    Return an mpv command-line to play BUT NOT record input_url.
    '''
    return ['mpv', '--vo=null', input_url]


def ffmpeg_cmdline(input_url, tee):
    '''
    Return a ffmpeg command to play and maybe record input_url.

    :param tee: if True, also save to disk.
    '''
    return ['ffmpeg',
            '-hide_banner',
            '-nostdin',
            '-i', f'async:{input_url}',
            *([] if not tee else
              ['-f', 'mpegts',
               '-c', 'copy',
               f'''./{datetime.now()
                              .replace(microsecond=0)
                              .isoformat()}.m2ts''']),
            '-f', 'alsa',
            'default']


def play(input_url, tee=False):
    '''
    Play input_url, optionally also saving to disk.
    '''
    subprocess.check_call(ffmpeg_cmdline(input_url, tee=tee))


def print_streams(streams):
    '''
    Pretty print streams.
    '''
    print(*sorted(streams), sep='\n')


def autocomplete(streams):
    '''
    List choices, and prompt with autocompletion one item from streams.
    '''
    print_streams(streams)
    # readline API doesn't make this undoable
    readline.parse_and_bind('tab: complete')
    try:
        old_delims = readline.get_completer_delims()
        readline.set_completer_delims('')
        try:
            old_completer = readline.get_completer()
            readline.set_completer(Completer(streams).complete)
            return streams[input('Playlist: ')]
        finally:
            readline.set_completer(old_completer)
    finally:
        readline.set_completer_delims(old_delims)


if __name__ == '__main__':
    from sys import exit

    args = argument_parser.parse_args()
    #streams = get_streams()
    streams = _COMPLETION_INDEX

    if args.list:
        print_streams(streams)
        exit()

    if args.url is not None:
        stream_url = args.url
    elif args.stream is None:
        try:
            stream_url = autocomplete(streams)
        except (KeyboardInterrupt, EOFError):
            exit(1)
    else:
        matches = {stream: url
                   for stream, url
                   in streams.items()
                   if all(map(stream.__contains__,
                              args.stream))}
        if not matches:
            exit(f'Not a valid stream: {" ".join(args.stream)}')
        elif len(matches) > 1:
            try:
                stream_url = autocomplete(matches)
            except (KeyboardInterrupt, EOFError):
                exit(1)
        else:
            stream_url = next(iter(matches.values()))

    play(stream_url, tee=args.tee)
