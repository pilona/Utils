#! /usr/bin/python3

from sys import exit
import gi; gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

if __name__ == "__main__":
    #dialog = Gtk.ColorChooserDialog()
    dialog = Gtk.ColorSelectionDialog()
    if dialog.run() == Gtk.ResponseType.OK:
        color = dialog.get_color_selection().get_current_rgba()
        red   = int(color.red * 255)
        green = int(color.green * 255)
        blue  = int(color.blue * 255)
        print("#{:02x}{:02x}{:02x}".format(red, green, blue))
    else:
        exit(1)
