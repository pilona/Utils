#! /usr/bin/env python3

from configparser import ConfigParser
import subprocess
import readline

import requests
from bs4 import BeautifulSoup


_STREAMS = 'http://music.cbc.ca/streams.aspx'

r = requests.get(_STREAMS)
r.raise_for_status()
s = BeautifulSoup(r.text, 'lxml')
playlists = {li.select_one('a.playStream').text:
               li.select_one('.streamUrl > a[href]')['href']
             for li
             in s.select('ul.streams > li')}

print(*sorted(playlists), sep='\n')

def completer(text, state):
    options = [playlist for playlist in playlists if text in playlist]
    if state < len(options):
        return options[state]
    else:
        return None

readline.parse_and_bind('tab: complete')
readline.set_completer(completer)

r = requests.get(playlists[input('Playlist: ')])
r.raise_for_status()

# Play first working stream
p = ConfigParser()
p.read_string(r.text)
for key, value in p['playlist'].items():
    if key.startswith('file') and subprocess.call(['mpv', value]) == 0:
        break
