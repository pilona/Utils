#! /usr/bin/env python3

from os import path, walk, execlp, environ
from string import Template
from argparse import ArgumentParser
from warnings import warn
from tempfile import TemporaryFile
from contextlib import suppress
from collections import defaultdict, OrderedDict

import re
import shlex
import pickle
import subprocess

from xdg import BaseDirectory
from xdg.DesktopEntry import DesktopEntry


dmenu_cache = path.join(BaseDirectory.xdg_cache_home, 'dmenu_desktop')


# TODO: path.normpath?
def parse_value(value):
    def callback(match):
        code = match.group()
        if code in 'nt$':
            return {'n': '\n',
                    't': '\t',
                    # convert \$ to $$ for string.Template
                    '$': '$$'}[code]
        else:
            # Taken care of further down the pipeline
            if code in ' $~':
                return '\\' + code
            if code not in '\"\'\\<>|&;*?#()`':
                warn('Unescaping bad escape \\' + code)
            return code[1]
    #return re.sub(r'(?<!\\)\\(?=[ \t\n\"\'\\<>~|&;$*?#()`])', '', word)
    value = re.sub(r'\\.', callback, value)

    # handles $foo, ${foo}, and $$
    value = Template(value).substitute(defaultdict(str, environ))

    # handles ~, ~foo, and \~
    value = path.expanduser(value)

    argv0, *args = shlex.split(value)
    assert '=' not in argv0
    return argv0, [arg
                   for arg
                   in map(percentfmt, args)
                   if arg is not False]


def percentfmt(word):
    if len(word) == 2 and word[0] == '%' and word[1] in 'dDnNvmfFuUk':
        warn('Removed field code')
        return False
    if word.endswith('%') and not word.endswith('%%'):
        warn('Unescaped percent')
    def callback(match):
        code = match.group()
        if code in 'dDnNvm':
            warn('Deprecated field code')
            return ''
        elif code in 'fFuU':
            warn('Not supporting user args to desktop entries.')
            warn('User can only enter desktop entry name.')
            return ''
        elif code == 'k':
            warn('Not implemented')
            return ''
        else:
            return {'i': entry.getIcon(),
                    'c': entry.getName()}
    return re.sub(r'%.', callback, word)


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
entry = entries[choice.strip()]
# TODO: StartupWMClass hint
# TODO: LC_MESSAGES
# TODO: Handle actions
# http://standards.freedesktop.org/desktop-entry-spec/latest/ar01s06.html
# http://standards.freedesktop.org/desktop-entry-spec/latest/ar01s05.html
# http://standards.freedesktop.org/desktop-entry-spec/latest/ar01s10.html
argv0, args = parse_value(entry.getExec())
if len(args) > 0:
    warn('Unparsed arguments "{}"'.format(args))
execlp(argv0, argv0)
