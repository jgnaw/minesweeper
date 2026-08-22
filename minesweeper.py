import random
from collections import deque


class Minesweeper:
    def __init__(self, rows, cols, num_mines):
        if num_mines >= rows * cols:
            raise ValueError("Too many mines for the board size")
        self.rows = rows
        self.cols = cols
        self.num_mines = num_mines
        # -1 marks a mine; 0..8 is the adjacent-mine count.
        self.board = [[0] * cols for _ in range(rows)]
        self.revealed = [[False] * cols for _ in range(rows)]
        self.flagged = [[False] * cols for _ in range(rows)]
        self.revealed_count = 0  # number of safe cells uncovered so far
        self.game_over = False   # set True once a mine is revealed
        self.mines_placed = False

    def neighbors(self, r, c):
        #yield up to 8 surrounding neighbors
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    yield nr, nc

    def place_mines(self, safe_r, safe_c):
        #determine safe cells (no mines guaranteed)
        safe = {(safe_r, safe_c)}
        safe.update(self.neighbors(safe_r, safe_c))

        #all other cells can have mines
        candidates = [(r, c) for r in range(self.rows) for c in range(self.cols)
            if (r, c) not in safe
        ]
        #randomly choose mine locations based on candidates
        mine_cells = random.sample(candidates, self.num_mines)

        #place mines accordingly
        for r, c in mine_cells:
            self.board[r][c] = -1

        self.count_adjacent()
        self.mines_placed = True

    def count_adjacent(self):
        #fill each revealed safe cell with the number of adjacent mines
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] == -1:
                    continue
                self.board[r][c] = sum(
                    1 for nr, nc in self.neighbors(r, c) if self.board[nr][nc] == -1)

    def reveal(self, r, c):
        """Reveal a cell. Returns False if it was a mine (game over), else True.

        Revealing a 0-cell flood-fills outward through connected 0-cells,
        also uncovering the numbered border that surrounds the empty region.
        """
        if self.game_over:
            return True  # game is frozen; ignore further clicks
        if self.flagged[r][c]:
            return True  # flagged cells are protected from clicks
        if self.revealed[r][c]:
            return True
        if self.board[r][c] == -1:
            self.revealed[r][c] = True
            self.game_over = True
            self.reveal_all_mines()
            return False  # boom

        queue = deque([(r, c)])
        self.revealed[r][c] = True
        self.revealed_count += 1
        while queue:
            cr, cc = queue.popleft()
            #if numbered cell found, stop
            if self.board[cr][cc] != 0:
                continue
            #if 0, loop through neighbors to continue revealing cells
            for nr, nc in self.neighbors(cr, cc):
                #if not flag and still unrevealed, reveal cell
                if not self.revealed[nr][nc] and not self.flagged[nr][nc]:
                    self.revealed[nr][nc] = True
                    self.revealed_count += 1
                    queue.append((nr, nc))
        return True

    def reveal_all_mines(self):
        #reveals all mines on a loss
        #flags on correctly marked mines are kept
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] == -1 and not self.flagged[r][c]:
                    self.revealed[r][c] = True

    def flag(self, r, c):
        #mark a cell with a flag
        if self.game_over:
            return
        if self.revealed[r][c]:
            return  # can't flag an already-open cell
        self.flagged[r][c] = not self.flagged[r][c]

    def won(self):
        #check for win, all safe cells are revealed
        safe_cells = self.rows * self.cols - self.num_mines
        return self.revealed_count == safe_cells

    def __str__(self):
        symbols = {-1: "*", 0: "."}
        return "\n".join(
            " ".join(symbols.get(cell, str(cell)) for cell in row)
            for row in self.board
        )

    def render(self):
        """Show the player's view: '#' hidden, 'F' flagged, revealed cells as-is."""
        symbols = {-1: "*", 0: "."}

        def cell(r, c):
            if self.revealed[r][c]:
                return symbols.get(self.board[r][c], str(self.board[r][c]))
            if self.flagged[r][c]:
                return "F"
            return "#"

        return "\n".join(
            " ".join(cell(r, c) for c in range(self.cols))
            for r in range(self.rows)
        )


def parse_command(text, rows, cols):
    """Turn a line of player input into ('quit'|'reveal'|'flag', r, c).

    Returns None (with a printed hint) if the line is malformed or out of bounds.
    Coordinates are 0-indexed: row first, then column.
    """
    tokens = text.split()
    if not tokens:
        return None

    verb = tokens[0].lower()
    if verb in ("q", "quit"):
        return "quit", None, None

    if verb not in ("r", "reveal", "f", "flag"):
        print("  ? commands: 'r ROW COL' reveal, 'f ROW COL' flag, 'q' quit")
        return None

    if len(tokens) != 3:
        print(f"  ? '{verb}' needs a row and a column, e.g. '{verb} 3 4'")
        return None

    try:
        r, c = int(tokens[1]), int(tokens[2])
    except ValueError:
        print("  ? row and column must be whole numbers")
        return None

    if not (0 <= r < rows and 0 <= c < cols):
        print(f"  ? out of bounds - row 0..{rows - 1}, col 0..{cols - 1}")
        return None

    action = "reveal" if verb in ("r", "reveal") else "flag"
    return action, r, c


def play(rows, cols, num_mines):
    """Run an interactive game of Minesweeper in the terminal."""
    game = Minesweeper(rows, cols, num_mines)
    print(f"Minesweeper - {rows}x{cols}, {num_mines} mines.")
    print("Commands: 'r ROW COL' reveal, 'f ROW COL' flag, 'q' quit. Coords are 0-indexed.\n")

    while True:
        # 1. DRAW
        print(game.render())

        # 2. CHECK - decided by the *previous* move's outcome
        if game.game_over:
            print("\n*** BOOM - you hit a mine. Game over. ***")
            break
        if game.won():
            print("\n*** You cleared the board. You win! ***")
            break

        # 3. READ
        try:
            line = input("\n> ")
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        command = parse_command(line, rows, cols)
        if command is None:
            print()
            continue

        action, r, c = command

        # 4. APPLY
        if action == "quit":
            print("Bye.")
            break
        elif action == "flag":
            game.flag(r, c)
        elif action == "reveal":
            # First reveal places mines, guaranteeing this cell is safe.
            if not game.mines_placed:
                game.place_mines(r, c)
            game.reveal(r, c)
        print()

def select_difficulty():
    options = {'b':(9, 9, 10), 'i':(16, 16, 40), 'e':(16, 30, 99)}
    prompt = "Select a difficulty: Beginner (b), Intermediate (i), Expert (e): "
    while True:
        try:
            dif = input(prompt).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nBye")
            raise SystemExit
        if dif in options:
            return options[dif]
        prompt = "Select a real difficulty: Beginner (b), Intermediate (i), Expert (e): "
            
if __name__ == "__main__":
    rows, cols, num_mines = select_difficulty()
    play(rows, cols, num_mines)
