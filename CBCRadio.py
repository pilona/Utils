#! /usr/bin/env python3

from configparser import ConfigParser
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


def play(playlist_url):
    r = requests.get(playlist_url)
    r.raise_for_status()

    # Play first working stream
    p = ConfigParser()
    p.read_string(r.text)
    for key, value in p['playlist'].items():
        if key.startswith('file') and subprocess.call(['mpv', value]) == 0:
            break


if __name__ == '__main__':
    playlists = get_playlists()
    print(*sorted(playlists), sep='\n')
    readline.parse_and_bind('tab: complete')
    readline.set_completer(new_completer(playlists))
    playlist_url = playlists[input('Playlist: ')]
    play(playlist_url)
