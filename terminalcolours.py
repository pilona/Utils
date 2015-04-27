#!/usr/bin/env python3
# Copyright (C) 2006 by Johannes Zellner, <johannes@zellner.org>
# modified by mac@calmar.ws to fit my output needs
# modified by crncosta@carloscosta.org to fit my output needs
# modified by alp@alexpilon.ca to not be so unidiomatic and slow

## obtained from:
## https://raw.githubusercontent.com/incitat/eran-dotfiles/master/bin/terminalcolors.py
## also see:
## http://vim.wikia.com/wiki/256_colors_in_vim

from sys import stdout
from curses import setupterm, tigetstr, tparm, COLOR_BLACK, COLOR_WHITE


setupterm()
setaf = lambda i: tparm(tigetstr('setaf'), i)
setab = lambda i: tparm(tigetstr('setab'), i)
black = setab(COLOR_BLACK)
write = stdout.buffer.write


def printcolour(i):
    write(setab(i))
    write(str(i).ljust(4).encode())
    write(black)


write(setaf(16))  # FIXME: Magic number
# Stock 8/16 colour palette.
for i in range(16):
    printcolour(i)
    if i % 8 == 7:
        write(b'\n')

write(b'\n')

# Non-grayscale from 256 colour palette.
for i in range(16, 232):
    printcolour(i)
    if i % 6 == 3:
        write(b'\n')

write(b'\n')

# Greyscale from 256 colour palette.
for i in range(232, 256):
    printcolour(i)
    if i % 6 == 3:
        write(b'\n')

write(b'\n')
write(setaf(COLOR_WHITE))
write(setab(COLOR_BLACK))
