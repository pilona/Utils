#! /bin/sh

# Derivative work
# https://raw.githubusercontent.com/incitat/eran-dotfiles/master/bin/terminalcolors.py
#
# Original credit:
# Copyright (C) 2006 by Johannes Zellner, <johannes@zellner.org>
# modified by mac@calmar.ws to fit my output needs
# modified by crncosta@carloscosta.org to fit my output needs

set -e


# Surprisingly effective optimization. Cuts runtime in half.
reset="$(tput setab 0)"
printcolour() {
    # Apparently, three printf calls makes this a bit slower.
    tput setab $1
    printf '%4d' $1
    printf '%s' "$reset"
}


tput setaf 16
# Basic 8/16 colours
for i in $(seq 0 15); do
    printcolour $i
    [ $((i % 8)) = 7 ] && echo
done

echo

# Non-greyscale upper 256 colours
for i in $(seq 16 231); do
    printcolour $i
    [ $((i % 6)) == 3 ] && echo
done

echo

# Greyscale upper 256 colours
for i in $(seq 232 255); do
    printcolour $i
    [ $((i % 6)) == 3 ] && echo
done

echo
tput setaf 7
tput setab 0
