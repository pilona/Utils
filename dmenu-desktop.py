#! /usr/bin/env python3

from os import path, walk, execlp, environ
from sys import exit
from argparse import ArgumentParser
from tempfile import TemporaryFile
from contextlib import suppress
from collections import defaultdict, OrderedDict

import shlex
import pickle
import subprocess

from xdg import BaseDirectory
from xdg.DesktopEntry import DesktopEntry

from gi.repository import Gio


dmenu_cache = path.join(BaseDirectory.xdg_cache_home, 'dmenu_desktop')


def cacher(it):
    with open(dmenu_cache, 'wb') as fp:
        for e in it:
            pickle.dump(e, fp)
            yield e


def get_runnable_entries():
    directories = list(BaseDirectory.load_data_paths('applications'))
    try:
        cachemt = path.getmtime(dmenu_cache)
    except FileNotFoundError:
        pass
    else:
        if all(path.getmtime(directory) <= cachemt
               for directory
               in directories):
            with suppress(EOFError):
                with open(dmenu_cache, 'rb') as fp:
                    while True:
                        yield pickle.load(fp)
            return
    yield from cacher(sorted((entry
                              for entry
                              in (DesktopEntry(path.join(dirpath, filename))
                                  for directory in directories
                                  for dirpath, _, filenames in walk(directory)
                                  for filename in filenames
                                  if filename.endswith('.desktop'))
                              if entry.getType() == 'Application' and
                                 entry.hasKey('Exec') and
                                 'true' not in {entry.getNoDisplay(),
                                                entry.getHidden()}),
                             key=lambda entry: entry.getName().casefold()))


parser = ArgumentParser(description='dmenu_run alternative only over desktop entries')
parser.add_argument('dmenuargs', nargs='*')
parser.add_argument('terminal', default='st', nargs='?')
args = parser.parse_args()

# TODO: Handle duplicates
entries = OrderedDict((entry.getName(), entry)
                      for entry
                      in get_runnable_entries())

with TemporaryFile() as fp:
    fp.write(b'\n'.join(map(str.encode, entries)))
    fp.flush()
    fp.seek(0)
    choice = subprocess.check_output(['dmenu'] + args.dmenuargs,
                                     universal_newlines=True,
                                     stdin=fp)

split = shlex.split(choice)
# Hack to be able to pass arguments to the desktop entries; longest prefix
# match on the desktop entry name.
# TODO: Pop up dmenu again to prompt?
for prefix_len in range(len(split), 0, -1):
    try:
        entry = entries[' '.join(split[:prefix_len])]
    except KeyError:
        pass
    else:
        launcher = Gio.DesktopAppInfo.new_from_filename(entry.filename)
        #launcher = Gio.DesktopAppInfo(**entry.content['Desktop Entry'])
        if launcher.launch_uris(split[prefix_len:]):
            exit()
        else:
            exit(1)
