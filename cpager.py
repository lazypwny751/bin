#!/usr/bin/env python
"""
Simple ncurses pad scrolling example.

Example usages: cpager.py -l {1..100}
                cpager.py -f ~/path/to/file
                cpager.py -s "some super long string with\n newlines..."

Use k/j/h/l to go up/down/left/right or q to quit.
"""

import cgitb
import curses
import curses.ascii
import os

from argparse import ArgumentParser, ArgumentTypeError
from lib.py.culor import addstr

os.environ.setdefault("ESCDELAY", "12")  # otherwise it takes an age!

# better debugging
cgitb.enable(format="text")


def chkfile(path):
    if os.path.isfile(path):
        return os.path.abspath(os.path.expanduser(path))

    raise ArgumentTypeError(f"{path} does not exist.")


def get_args():
    parser = ArgumentParser(description=f"Curses Pager Experiments")
    parser.add_argument("-f", "--file", type=chkfile, help="file to page")
    parser.add_argument("-l", "--list", nargs="+", help="list to page")
    parser.add_argument("-s", "--string", help=f"long string to page")
    return parser.parse_args()


def event_loop(stdscr, lines):
    maxy, maxx = stdscr.getmaxyx()
    longest = len(max(lines, key=len))
    pad = curses.newpad(len(lines) + 1, longest + 1)
    pad.keypad(True)  # use function keys
    curses.curs_set(0)  # hide the cursor
    curses.use_default_colors()  # https://stackoverflow.com/a/44015131
    pminrow = 0  # pad row to start displaying contents at
    pmincol = 0  # pad column to start displaying contents at
    while True:
        # draw lines
        for idx, line in enumerate(lines):
            # pad.addstr(idx, 0, line)
            addstr(pad, idx, 0, line)

        # refresh components
        stdscr.noutrefresh()
        pad.noutrefresh(pminrow, pmincol, 0, 0, maxy - 1, maxx - 1)
        curses.doupdate()

        # react to input
        key = stdscr.getch()

        if key == ord("q") or key == curses.ascii.ESC:
            break

        if key == ord("k") or key == curses.KEY_UP:
            if pminrow > 0:
                pminrow -= 1
        elif key == ord("j") or key == curses.KEY_DOWN:
            if pminrow < len(lines) - maxy:
                pminrow += 1
        elif key == ord("h") or key == curses.KEY_LEFT:
            if pmincol > 0:
                pmincol -= 1
        elif key == ord("l") or key == curses.KEY_RIGHT:
            if pmincol < longest - maxx:
                pmincol += 1
        elif key == curses.KEY_RESIZE:
            stdscr.erase()
            pad.erase()
            maxy, maxx = stdscr.getmaxyx()


def parse_newlines(lines):
    for l in lines:
        if "\\n" in l:
            idx = lines.index(l)
            new_elements = l.split("\\n")
            lines.remove(l)
            for e in new_elements:
                lines.insert(idx, e)
                idx += 1

    return lines


def main():
    args = get_args()

    if args.file:
        path = os.path.abspath(os.path.expanduser(args.file))
        with open(path, "r") as file:
            lines = file.readlines()
    elif args.list:
        lines = parse_newlines(args.list)
    elif args.string:
        lines = args.string.split("\n")

    curses.wrapper(event_loop, lines)


if __name__ == "__main__":
    main()
