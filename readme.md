# bitsense

This is a game for me or anyone to practice bin and hex conversion speed. It helps in computing exams if one has a good intuition with it. Also I see it as a good chance to practice TUI as I use tools with TUI everyday but don't know how to write one. I may also make a WebUI version as it is also a good game to compete with friends.

## Design

Basic Features

1. bin to hex
2. hex to bin

Progress Features

1. on time speed
bit per second

2. historical data
progress chart

calc logic

loggin logic
possible and easy way: limit time and limit bits
ideal way is get in and type

## TUI prototype (bin → hex)

Quick demo built with Textual to show how a TUI could work.

```
pip install textual
python bin2hex_tui.py
```

Type a binary string (spaces allowed) and press Enter or hit Convert to see the hex output. Handles basic validation so you can extend it into a full game loop later.

## Comparing TUI approaches

Two side-by-side demos that highlight a real difference: updating a smooth timer/progress bar while the user is typing.

### prompt_toolkit (high-level input + smooth redraw)

```
python timed_round_prompt_toolkit.py
```

### curses (classic; manual input handling for smooth redraw)

```
python timed_round_curses.py
```
