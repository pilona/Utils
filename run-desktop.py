#! /usr/bin/env python3

# Derived from http://askubuntu.com/questions/5172/running-a-desktop-file-in-the-terminal
from argparse import ArgumentParser, OPTIONAL

argument_parser = ArgumentParser('.desktop file and autostart utility')
mutex_groups = argument_parser.add_mutually_exclusive_group()
mutex_groups.add_argument('-a', '--autostart', action='store_true')
mutex_groups.add_argument('-f', '--desktop-file')
argument_parser.add_argument('args', nargs=OPTIONAL, default=[])


def launch_desktop_file(desktop_file, *args):
    launcher = Gio.DesktopAppInfo.new_from_filename(desktop_file)
    launcher.launch_uris(args)


__all__ = {'argument_parser', 'launch_desktop_file'}

if __name__ == '__main__':
    from glob import glob
    from os import path

    from gi.repository import Gio
    from xdg import BaseDirectory

    args = argument_parser.parse_args()

    if args.autostart:
        for directory in BaseDirectory.load_config_paths('autostart'):
            for dentry in glob(path.join(directory, '*.desktop')):
                launch_desktop_file(dentry)
    elif args.desktop_file:
        launch_desktop_file(args.desktop_file, *args.args)
    else:
        exit(argument_parser.print_help())
