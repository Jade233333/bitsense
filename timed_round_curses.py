#!/usr/bin/env python3
"""
Timed Bin → Hex round (curses).

This demonstrates what you typically have to do in curses: to animate a timer
while still letting the user type, you usually write your own small line editor
(buffer, backspace handling, cursor, etc.) using getch() in nodelay mode.

Run:
  python timed_round_curses.py

Keys:
  Enter  submit answer
  q      quit
"""

from __future__ import annotations

import curses
import random
import time

BITS = 8
MAX_VAL = (1 << BITS) - 1
HEX_WIDTH = (BITS + 3) // 4
ROUND_SECONDS = 10.0


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


def is_valid_hex_so_far(raw: str) -> bool:
    s = raw.strip()
    if s.lower().startswith("0x"):
        s = s[2:]
    return (not s) or all(c in "0123456789abcdefABCDEF" for c in s)


def run(stdscr) -> None:
    stdscr.nodelay(True)
    stdscr.keypad(True)
    try:
        curses.curs_set(1)
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
        curses.init_pair(1, curses.COLOR_GREEN, -1)  # ok
        curses.init_pair(2, curses.COLOR_RED, -1)  # error
        curses.init_pair(3, curses.COLOR_CYAN, -1)  # accents
        curses.init_pair(4, curses.COLOR_YELLOW, -1)  # warning/validation
        stdscr.bkgd(" ", curses.color_pair(0))

    total = 0
    correct = 0
    streak = 0
    message = ("Type hex and press Enter.", 0)

    def new_round():
        return random.randint(0, MAX_VAL), time.monotonic()

    n, round_start = new_round()
    b = to_bin(n)
    correct_h = to_hex(n)
    buf = ""

    frame_s = 1 / 30
    while True:
        now = time.monotonic()
        remaining = max(0.0, ROUND_SECONDS - (now - round_start))

        key = stdscr.getch()
        if key in (ord("q"), ord("Q")):
            return

        if key != -1:
            if key in (curses.KEY_ENTER, 10, 13):
                # submit
                total += 1
                try:
                    val = parse_hex_answer(buf)
                except ValueError:
                    streak = 0
                    message = (f"Invalid. Correct: {correct_h}", 2)
                else:
                    if val == n:
                        correct += 1
                        streak += 1
                        message = ("Correct.", 1)
                    else:
                        streak = 0
                        message = (f"Wrong. Correct: {correct_h}", 2)

                n, round_start = new_round()
                b = to_bin(n)
                correct_h = to_hex(n)
                buf = ""

            elif key in (curses.KEY_BACKSPACE, 127, 8):
                buf = buf[:-1]
            else:
                # Keep it simple: append printable ASCII only.
                if 32 <= key <= 126:
                    buf += chr(key)

        # timeout triggers a new round (counts as attempt)
        if remaining <= 0.0:
            total += 1
            streak = 0
            message = (f"Time's up. Correct: {correct_h}", 2)
            n, round_start = new_round()
            b = to_bin(n)
            correct_h = to_hex(n)
            buf = ""
            remaining = ROUND_SECONDS

        rows, cols = stdscr.getmaxyx()
        bar_width = 36
        frac = remaining / ROUND_SECONDS if ROUND_SECONDS else 0.0
        filled = int(round(frac * bar_width))
        empty = bar_width - filled

        # Layout within a centered box.
        title = "Timed Bin → Hex (curses)"
        subtitle = "Timer animates while typing (manual input buffer). Press q to quit."
        prompt = f"BIN {b} → HEX = "
        validation = "Live check: hex chars only (0-9, a-f), optional 0x."
        accuracy = (correct / total * 100.0) if total else 0.0
        stats = f"Stats: {correct}/{total} ({accuracy:0.0f}%) streak {streak}"
        msg_text, msg_kind = message

        inner_width = max(
            len(title),
            len(subtitle),
            len(prompt) + max(8, len(buf)),
            len(validation),
            len("Time: 00.0s [" + ("█" * bar_width) + "]"),
            len(stats),
            len(msg_text),
        )
        inner_width = min(inner_width, max(20, cols - 6))
        box_w = inner_width + 4  # borders + padding
        box_h = 12
        top = max(0, (rows - box_h) // 2)
        left = max(0, (cols - box_w) // 2)

        stdscr.erase()

        # Border characters (unicode; fall back to ASCII if terminal can't draw them).
        try:
            tl, tr, bl, br, hz, vt = "┌", "┐", "└", "┘", "─", "│"
            stdscr.addstr(top, left, tl + (hz * (box_w - 2)) + tr)
            for r in range(1, box_h - 1):
                stdscr.addstr(top + r, left, vt)
                stdscr.addstr(top + r, left + box_w - 1, vt)
            stdscr.addstr(top + box_h - 1, left, bl + (hz * (box_w - 2)) + br)
        except curses.error:
            tl, tr, bl, br, hz, vt = "+", "+", "+", "+", "-", "|"
            stdscr.addstr(top, left, tl + (hz * (box_w - 2)) + tr)
            for r in range(1, box_h - 1):
                stdscr.addstr(top + r, left, vt)
                stdscr.addstr(top + r, left + box_w - 1, vt)
            stdscr.addstr(top + box_h - 1, left, bl + (hz * (box_w - 2)) + br)

        def write_line(row: int, text: str, attr: int = 0) -> None:
            y = top + 1 + row
            x = left + 2
            clipped = text[:inner_width].ljust(inner_width)
            try:
                stdscr.addstr(y, x, clipped, attr)
            except curses.error:
                return

        title_attr = curses.A_BOLD | (curses.color_pair(3) if has_colors else 0)
        write_line(0, title.center(inner_width), title_attr)
        write_line(1, subtitle.center(inner_width), curses.color_pair(0))

        # Prompt + buffer (left-aligned inside centered box).
        q_attr = curses.A_BOLD
        write_line(3, prompt, q_attr)
        valid_attr = curses.color_pair(0)
        if has_colors and not is_valid_hex_so_far(buf):
            valid_attr = curses.color_pair(4) | curses.A_BOLD
        try:
            stdscr.addstr(top + 1 + 3, left + 2 + len(prompt), buf[: max(0, inner_width - len(prompt))], valid_attr)
        except curses.error:
            pass

        # Cursor at end of buffer.
        try:
            cursor_x = left + 2 + len(prompt) + min(len(buf), max(0, inner_width - len(prompt)))
            stdscr.move(top + 1 + 3, cursor_x)
        except curses.error:
            pass

        time_line = f"Time: {remaining:4.1f}s "
        bar = "[" + ("█" * filled) + (" " * empty) + "]"
        write_line(5, (time_line + bar).center(inner_width), curses.A_BOLD)

        write_line(6, validation.center(inner_width), curses.color_pair(0))
        write_line(7, stats.center(inner_width), curses.color_pair(0))

        msg_attr = 0
        if has_colors:
            if msg_kind == 1:
                msg_attr = curses.color_pair(1) | curses.A_BOLD
            elif msg_kind == 2:
                msg_attr = curses.color_pair(2) | curses.A_BOLD
        write_line(9, msg_text.center(inner_width), msg_attr)

        stdscr.refresh()
        time.sleep(frame_s)


def main() -> None:
    curses.wrapper(run)


if __name__ == "__main__":
    main()
