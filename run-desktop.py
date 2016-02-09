#! /usr/bin/env python3

# Derived from http://askubuntu.com/questions/5172/running-a-desktop-file-in-the-terminal

from gi.repository import Gio
from sys import argv

_, desktop, *uris = argv
launcher = Gio.DesktopAppInfo.new_from_filename(desktop)
launcher.launch_uris(uris)
