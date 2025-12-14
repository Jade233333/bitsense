#!/usr/bin/env python3
"""
Bin → Hex trainer (curses prototype).

Run:
  python bin2hex_curses.py

Notes:
  - On Linux/macOS, Python's stdlib `curses` uses system `ncurses`.
  - On Windows, use `pip install windows-curses` first (PDCurses wrapper).
"""

from __future__ import annotations

import curses
import random

BITS = 4  # change to 4 if you want single hex-digit inputs
MAX_VAL = (1 << BITS) - 1
HEX_WIDTH = (BITS + 3) // 4  # 4 bits per hex digit


def to_hex(n: int) -> str:
    return f"{n:0{HEX_WIDTH}X}"


def to_bin(n: int) -> str:
    return f"{n:0{BITS}b}"


def parse_hex_answer(raw: str) -> int:
    ans = raw.strip()
    if ans.lower().startswith("0x"):
        ans = ans[2:]
    if not ans or any(c not in "0123456789abcdefABCDEF" for c in ans):
        raise ValueError("Invalid hex input.")
    return int(ans, 16)


def run(stdscr) -> None:
    try:
        curses.curs_set(1)
    except curses.error:
        pass
    stdscr.nodelay(False)
    stdscr.keypad(True)

    has_colors = curses.has_colors()
    if has_colors:
        curses.start_color()
        try:
            curses.use_default_colors()
        except curses.error:
            has_colors = False

    if has_colors:
        curses.init_pair(1, curses.COLOR_GREEN, -1)  # correct
        curses.init_pair(2, curses.COLOR_RED, -1)  # wrong / error
        curses.init_pair(3, curses.COLOR_CYAN, -1)  # title
        stdscr.bkgd(" ", curses.color_pair(0))

    while True:
        n = random.randint(0, MAX_VAL)
        b = to_bin(n)
        correct_h = to_hex(n)

        stdscr.erase()
        title_attr = curses.color_pair(3) | curses.A_BOLD if has_colors else curses.A_BOLD
        stdscr.addstr(
            0,
            0,
            f"Bin → Hex trainer ({BITS}-bit values). Type 'q' to quit.",
            title_attr,
        )
        stdscr.addstr(2, 0, f"BIN {b} → HEX = ")
        stdscr.refresh()

        curses.echo()
        try:
            raw_bytes = stdscr.getstr(2, len(f"BIN {b} → HEX = "), 64)
        finally:
            curses.noecho()

        raw = raw_bytes.decode(errors="replace").strip()
        if raw.lower() == "q":
            return

        try:
            val = parse_hex_answer(raw)
        except ValueError:
            err_attr = curses.color_pair(2) | curses.A_BOLD if has_colors else curses.A_BOLD
            stdscr.addstr(4, 0, "Invalid input. ", err_attr)
            stdscr.addstr(f"Correct: {correct_h}")
            stdscr.addstr(6, 0, "Press any key for next…")
            stdscr.getch()
            continue

        if val == n:
            ok_attr = curses.color_pair(1) | curses.A_BOLD if has_colors else curses.A_BOLD
            stdscr.addstr(4, 0, "Correct.", ok_attr)
        else:
            err_attr = curses.color_pair(2) | curses.A_BOLD if has_colors else curses.A_BOLD
            stdscr.addstr(4, 0, "Wrong. ", err_attr)
            stdscr.addstr(f"Correct: {correct_h}")

        stdscr.addstr(6, 0, "Press any key for next…")
        stdscr.getch()


def main() -> None:
    curses.wrapper(run)


if __name__ == "__main__":
    main()
