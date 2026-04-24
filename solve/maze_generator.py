import random
from typing import Optional, List, Tuple, Set

N, E, S, W = 1, 2, 4, 8

DIRS = {
    "N": (0, -1, N, S),
    "E": (1, 0, E, W),
    "S": (0, 1, S, N),
    "W": (-1, 0, W, E),
}

class Maze:
    def __init__(self, w: int, h: int):
        self.w = w
        self.h = h
        self.grid: List[List[int]] = [
            [15 for _ in range(w)] for _ in range(h)
        ]

    def cell(self, x: int, y: int) -> int:
        return self.grid[y][x]

    def update(self, x: int, y: int, value: int):
        self.grid[y][x] = value

class MazeGenerator:
    def __init__(self, w: int, h: int, seed: Optional[int] = None, perfect: bool = True):
        self.w = w
        self.h = h
        self.rng = random.Random(seed)
        self.perfect = perfect

    def inside(self, x: int, y: int) -> bool:
        return 0 <= x < self.w and 0 <= y < self.h

    def break_wall(self, maze: Maze, x: int, y: int, d: str):
        dx, dy, bit, opp = DIRS[d]
        nx, ny = x + dx, y + dy
        if not self.inside(nx, ny):
            return
        maze.update(x, y, maze.cell(x, y) & ~bit)
        maze.update(nx, ny, maze.cell(nx, ny) & ~opp)

    def _get_42_pattern(self) -> List[str]:
        small = [
            "#.#.###",
            "#.#...#",
            "###.###",
            "..#.#..",
            "..#.###",
        ]
        medium = [
            "#..#.####",
            "#..#....#",
            "####.####",
            "...#.#...",
            "...#.####",
            ".......#.",
        ]
        big = [
            "#...#.#####",
            "#...#.....#",
            "#...#.....#",
            "#####.#####",
            "....#.#....",
            "....#.#....",
            "....#.#####",
        ]
        if self.w < 25 or self.h < 20:
            return small
        elif self.w < 45 or self.h < 30:
            return medium
        else:
            return big

    def _build_42_coords(self) -> Set[Tuple[int, int]]:
        pattern = self._get_42_pattern()
        ph = len(pattern)
        pw = len(pattern[0])
        ox = (self.w - pw) // 2
        oy = (self.h - ph) // 2
        coords = set()
        for y in range(ph):
            for x in range(pw):
                if pattern[y][x] == "#":
                    coords.add((ox + x, oy + y))
        return coords

    def _apply_42(self, maze: Maze, coords: Set[Tuple[int, int]]):
        for x, y in coords:
            maze.update(x, y, 15)

    def _add_loops(self, maze: Maze):
        attempts = (self.w * self.h) // 8
        for _ in range(attempts):
            x = self.rng.randrange(self.w)
            y = self.rng.randrange(self.h)
            d = self.rng.choice(list(DIRS.keys()))
            self.break_wall(maze, x, y, d)

    def generate(self, start: Tuple[int, int]) -> Maze:
        if not self.inside(*start):
            raise ValueError("Invalid start position")
        maze = Maze(self.w, self.h)
        blocked = set()
        try:
            blocked = self._build_42_coords()
        except:
            blocked = set()
        if start in blocked:
            raise ValueError("Start inside 42")
        visited: Set[Tuple[int, int]] = set()
        stack: List[Tuple[int, int]] = [start]
        visited.add(start)
        while stack:
            x, y = stack[-1]
            neighbors = []
            for d, (dx, dy, *_ ) in DIRS.items():
                nx, ny = x + dx, y + dy
                if not self.inside(nx, ny):
                    continue
                if (nx, ny) in visited:
                    continue
                if (nx, ny) in blocked:
                    continue
                neighbors.append((nx, ny, d))
            if not neighbors:
                stack.pop()
                continue
            nx, ny, d = self.rng.choice(neighbors)
            self.break_wall(maze, x, y, d)
            visited.add((nx, ny))
            stack.append((nx, ny))
        if not self.perfect:
            self._add_loops(maze)
        self._apply_42(maze, blocked)
        return maze

def export_maze(maze, entry, exit, path, filename):
    with open(filename, "w") as f:
        for row in maze.grid:
            f.write("".join(format(cell, "X") for cell in row) + "\n")
        f.write("\n")
        f.write(f"{entry[0]},{entry[1]}\n")
        f.write(f"{exit[0]},{exit[1]}\n")
        f.write("".join(path) + "\n")
