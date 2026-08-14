# Minesweeper

Minesweeper built from scratch as a learning project — a terminal version in Python
and a self-contained browser version. No dependencies, no framework.

## Play it

**Terminal (Python 3):**

```bash
python minesweeper.py
```

Commands are `r ROW COL` to reveal, `f ROW COL` to flag, `q` to quit.
Coordinates are 0-indexed, row first. Default board is 9x9 with 10 mines;
`play(rows, cols, num_mines)` takes any size.

```
# # # # #        > r 2 3
# # # # #
# # # # #        .  reveal a cell   F  flagged
# # # # #        #  hidden          *  mine
# # # # #        1-8 adjacent mine count
```

**Browser:** open `minesweeper_web.html` in any browser. Single file, dark/light aware.

## How it works

Three algorithms carry the game, all in `minesweeper.py`:

- **First-click-safe board generation** (`place_mines`) — mines are placed *after* the
  opening click, with the clicked cell and its 8 neighbors excluded from the candidate
  pool, so you never lose on move one. `random.sample` draws distinct cells in one shot
  rather than looping and re-rolling collisions.
- **Flood-fill reveal** (`reveal`) — BFS with a `deque`. Clicking a `0` cascades through
  connected empty cells and uncovers the numbered border around them; numbered cells are
  revealed but don't propagate. Iterative rather than recursive so a large empty region
  can't blow Python's recursion limit.
- **O(1) win detection** (`won`) — a running `revealed_count` compared against
  `rows * cols - num_mines`, instead of rescanning the grid after every move.

Board cells are encoded `-1` for a mine and `0..8` for the adjacent-mine count, with
parallel `revealed` and `flagged` grids holding player-visible state. Game rules live in
the `Minesweeper` class; all terminal I/O lives in `play()` and `parse_command()`, which
validates every line so the class only ever receives well-formed moves.

`NOTES.md` has the longer write-up: the design decisions, the BFS-vs-DFS reasoning, and
the correctness traps found along the way.

## Still to build

- Timer / move counter
- Difficulty selection at startup
