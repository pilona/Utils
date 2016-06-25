#! /usr/bin/env python3

from configparser import ConfigParser
from datetime import datetime
import subprocess
import readline

import requests
from bs4 import BeautifulSoup


_STREAMS = 'http://music.cbc.ca/streams.aspx'


def get_playlists():
    r = requests.get(_STREAMS)
    r.raise_for_status()
    s = BeautifulSoup(r.text, 'lxml')
    return {li.select_one('a.playStream').text:
            li.select_one('.streamUrl > a[href]')['href']
            for li
            in s.select('ul.streams > li')}


def new_completer(playlist):
    def completer(text, state):
        nonlocal playlist
        options = [playlist for playlist in playlists if text in playlist]
        if state < len(options):
            return options[state]
        else:
            return None
    return completer


def play(playlist_url, tee=False):
    r = requests.get(playlist_url)
    r.raise_for_status()

    # Play first working stream
    p = ConfigParser()
    p.read_string(r.text)
    for key, value in p['playlist'].items():
        if (key.startswith('file') and
            subprocess.call(['ffmpeg',
                             '-nostdin',
                             '-i', 'async:' + value] +
                            # Yes, check by identity
                            ([] if not tee else
                             ['-f', 'mpegts',
                              '-c', 'copy',
                              './' +
                                datetime.now()
                                        .replace(microsecond=0)
                                        .isoformat() +
                                '.m2ts']) +
                            ['-f', 'alsa',
                             'default']) == 0):
            break


if __name__ == '__main__':
    from argparse import ArgumentParser
    from sys import exit

    ap = ArgumentParser('Play/download CBC Radio playlists')
    ap.add_argument('-l', '--list', action='store_true')
    ap.add_argument('-t', '--tee', action='store_true')
    ap.add_argument('playlist', nargs='?')
    args = ap.parse_args()

    playlists = get_playlists()

    if args.list:
        print(*sorted(playlists), sep='\n')
        exit()

    if args.playlist is None:
        print(*sorted(playlists), sep='\n')
        readline.parse_and_bind('tab: complete')
        readline.set_completer(new_completer(playlists))
        playlist_url = playlists[input('Playlist: ')]
    else:
        try:
            playlist_url = playlists[args.playlist]
        except KeyError:
            exit('Not a valid playlist: ' + args.playlist)

    play(playlist_url, tee=args.tee)
