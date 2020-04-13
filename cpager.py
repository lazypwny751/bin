#!/usr/bin/env python
"""
Simple ncurses pad scrolling example.

Example usage: cpager.py "super long string"

Use j/k to go down/up or q to quit.
"""

import cgitb
import curses
import sys

# better debugging
cgitb.enable(format="text")


def main(stdscr, line):
    maxy, maxx = stdscr.getmaxyx()
    pad = curses.newpad(maxy, maxx)
    pad.keypad(True)  # use function keys
    curses.curs_set(0)  # hide the cursor
    pminrow = 0  # pad row to start displaying contents at
    while True:
        if len(line) >= maxx:
            split_lines = [line[i : i + maxx] for i in range(0, len(line), maxx)]
            max_lines = len(split_lines)
            pad.resize(max_lines, maxx)
            for idx, line in enumerate(split_lines):
                pad.addstr(idx, 0, line)
        else:
            pad.addstr(0, 0, line)

        # refresh components
        stdscr.noutrefresh()
        pad.noutrefresh(pminrow, 0, 0, 0, maxy - 1, maxx - 1)
        curses.doupdate()

        # react to input
        key = stdscr.getch()

        if key == ord("q"):
            break

        if key == ord("k"):
            if pminrow > 0:
                pminrow -= 1
        elif key == ord("j"):
            if pminrow < max_lines - maxy:
                pminrow += 1
        elif key == curses.KEY_RESIZE:
            stdscr.erase()
            pad.erase()
            maxy, maxx = stdscr.getmaxyx()


if __name__ == "__main__":
    curses.wrapper(main, sys.argv[1])
