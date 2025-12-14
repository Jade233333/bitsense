#!/usr/bin/env python3
"""
Smooth progress bar demo (curses).

Run:
  python progress_bar_curses.py

Keys:
  q  quit
"""

from __future__ import annotations

import curses
import time


def ping_pong_fraction(start: float, duration_s: float) -> float:
    t = (time.monotonic() - start) / duration_s
    phase = t % 2.0
    return phase if phase <= 1.0 else 2.0 - phase


def run(stdscr) -> None:
    stdscr.nodelay(True)
    stdscr.keypad(True)
    try:
        curses.curs_set(0)
    except curses.error:
        pass

    has_colors = curses.has_colors()
    if has_colors:
        curses.start_color()
        try:
            curses.use_default_colors()
        except curses.error:
            has_colors = False

    if has_colors:
        curses.init_pair(1, curses.COLOR_CYAN, -1)
        curses.init_pair(2, curses.COLOR_WHITE, -1)
        stdscr.bkgd(" ", curses.color_pair(0))

    start = time.monotonic()
    duration_s = 5.0
    frame_s = 1 / 30

    while True:
        key = stdscr.getch()
        if key in (ord("q"), ord("Q")):
            return

        rows, cols = stdscr.getmaxyx()
        bar_width = max(10, cols - 18)
        frac = ping_pong_fraction(start, duration_s)
        filled = int(round(frac * bar_width))
        empty = bar_width - filled
        percent = int(round(frac * 100))

        stdscr.erase()
        title_attr = curses.A_BOLD | (curses.color_pair(2) if has_colors else 0)
        stdscr.addstr(0, 0, "Smooth progress bar (curses)", title_attr)
        stdscr.addstr(1, 0, "Press q to quit. Animates at ~30 FPS.")

        bar_attr = curses.color_pair(1) if has_colors else 0
        stdscr.addstr(3, 0, "[")
        stdscr.addstr(3, 1, "█" * filled, bar_attr)
        stdscr.addstr(3, 1 + filled, " " * empty)
        stdscr.addstr(3, 1 + bar_width, "] ")
        stdscr.addstr(f"{percent:3d}%")

        if rows >= 6:
            stdscr.addstr(5, 0, f"Terminal size: {cols}x{rows}")

        stdscr.refresh()
        time.sleep(frame_s)


def main() -> None:
    curses.wrapper(run)


if __name__ == "__main__":
    main()
