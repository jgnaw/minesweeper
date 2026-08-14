# Minesweeper Build — Session Notes

A learning session building a Minesweeper board in Python, plus the algorithms behind it.

## What we built (`minesweeper.py`)

A `Minesweeper` class with three core algorithms:

1. **Board generation** — `place_mines(safe_r, safe_c)`
2. **Flood-fill reveal (BFS)** — `reveal(r, c)`
3. **Win detection (running counter)** — `is_won()`

Cell encoding: `-1` = mine, `0..8` = adjacent-mine count. A parallel `revealed` grid
tracks player-visible state.

## Key design decisions

### Board generation
- **First click is always safe:** mines are placed *after* the first click, excluding
  the clicked cell *and its 8 neighbors* from the candidate pool.
- **`random.sample(candidates, num_mines)`** picks distinct cells in one shot — avoids the
  classic bug where a naive loop picks the same cell twice and places too few mines.
- Counts are filled in a separate `_count_adjacent()` sweep for readability.
- A shared `_neighbors(r, c)` helper does bounds-checking in one place.

### Flood-fill reveal (BFS)
The reveal rule:
- Click a **mine** -> game over.
- Click a **numbered cell (1-8)** -> reveal just that one cell (it's a boundary wall).
- Click a **0-cell** -> reveal it and cascade to all 8 neighbors; only *other 0-cells*
  keep the cascade going. Numbered cells are revealed but do NOT propagate.

Two correctness details:
- **Expansion guard is inside the loop:** only fan out from a popped cell if it's a `0`.
- **Mark visited at enqueue time, not dequeue time** — prevents the same cell being queued
  multiple times.

### BFS vs DFS (the concept)
- Same problem as Number of Islands; both visit every reachable connected cell.
- **DFS = stack (LIFO)** — often the recursion call stack; plunges deep down one path.
- **BFS = queue (FIFO)** — "add to the back, take from the front"; ripples outward in rings
  of increasing distance.
- The *only* code difference between iterative versions: `queue.popleft()` (front, BFS) vs
  `stack.pop()` (back, DFS).
- Chose BFS here to avoid Python's ~1000-frame recursion limit on large empty regions.

### Win detection (running counter)
- Win condition: **every non-mine cell is revealed** (flags are irrelevant to winning).
- `revealed_count == rows*cols - num_mines`, checked in O(1).
- Counter is only incremented in the two flood-fill spots, never in the mine branch.
- **Safe by construction:** the start cell is guarded against being a mine, and the flood
  fill only expands from 0-cells (which have zero adjacent mines), so no mine is ever counted.

### Flags & game-over state
- **`self.game_over`** flag, checked as the *first* line of `reveal` — a click after a
  loss can't restart a flood-fill. Set to `True` in the mine branch.
- **`self.flagged`** parallel grid + **`flag(r, c)`** toggle. Three interaction traps:
  1. Can't flag an already-revealed cell.
  2. `reveal` ignores flagged cells (flags protect a suspected mine from a stray click).
  3. The flood-fill also stops at flagged cells — flag protection is consistent even
     against an automatic cascade.
- Flags never touch `revealed_count`, so `is_won()` is unaffected (as designed).
- `render()` shows `F` for flagged cells.

### Reveal-all-mines on loss
- **`_reveal_all_mines()`** sweeps the board in the mine branch of `reveal`.
- **The trap:** it must NOT increment `revealed_count` (mines aren't safe cells) or a
  loss could falsely read as a win. It sets `revealed` directly, same as the mine branch.
- **Design choice:** skips cells you flagged, so a *correctly*-flagged mine stays `F`
  instead of being overwritten with `*` — you keep the credit (matches classic Minesweeper).

### Playable input loop (`play()` + `parse_command()`)
The I/O layer, kept **separate** from the `Minesweeper` class (class = rules, loop = human).
A REPL-style loop of four steps, forever until win/lose/quit:
1. **DRAW** — `print(game.render())`
2. **CHECK** — `game_over` (loss) then `is_won()` (win); checked *before* reading input,
   so it reflects the move just made. Order matters: loss before win.
3. **READ** — `input()`, wrapped so Ctrl+C / Ctrl+D exit cleanly.
4. **APPLY** — `parse_command()` then call `flag`/`reveal`.

Key points:
- **`parse_command()` is the validation firewall:** empty lines, wrong verb, wrong arg
  count, non-numbers, out-of-bounds are all caught here and re-prompted. The class only
  ever receives well-formed commands and never has to defend itself.
- **First-click safety lives in the loop:** the first `reveal` triggers `place_mines(r, c)`
  first (guarded by `_mines_placed`), so the opening click is always safe.
- Command grammar: `r ROW COL` reveal, `f ROW COL` flag, `q` quit. 0-indexed.
- **Windows gotcha:** avoid non-ASCII (em-dashes) in `print` strings — cp1252 console
  mangles them (`�`) or errors. Use plain hyphens.

## Next steps (not yet built)
- Timer / move counter
- Difficulty selection at startup (`play(rows, cols, num_mines)` already parametrized)
