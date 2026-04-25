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
        #######
        # added stamp42 for coordinates on the logo
        #######
        self.stamp42: set[Tuple[int, int]] = set()

    def cell(self, x: int, y: int) -> int:
        return self.grid[y][x]

    def update(self, x: int, y: int, value: int):
        self.grid[y][x] = value


class MazeGenerator:
    def __init__(
            self, width: int,
            height: int,
            seed: Optional[int] = None,
            perfect: bool = True
            ):
        self.w = width
        self.h = height
        self.rng = random.Random(seed)
        self.perfect = perfect
        self.current_seed: int | None = seed

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

    def can_fit_42(self) -> bool:
        #########
        # VERIFY IF POSSIBLE TO ADD 42 LOGO
        #########
        pattern = self._get_42_pattern()
        ph = len(pattern)
        pw = len(pattern[0])
        return self.w >= pw and self.h >= ph

    def _apply_42(self, maze: Maze, coords: Set[Tuple[int, int]]):
        for x, y in coords:
            maze.stamp42 = coords
        #########
        # Added a stamp42 coordinates so renderer.py can fill it
        #########
        

    def _add_loops(self, maze: Maze):
        attempts = (self.w * self.h) // 8
        blocked = maze.stamp42

        for _ in range(attempts):
            x = self.rng.randrange(self.w)
            y = self.rng.randrange(self.h)

            d = self.rng.choice(list(DIRS))
            dx, dy, bit, opp = DIRS[d]
            nx, ny = x + dx, y + dy

            if not self.inside(nx, ny):
                continue

            cell = maze.cell(x, y)
            ncell = maze.cell(nx, ny)

            if (x, y) in blocked or (nx, ny) in blocked:
                continue
            #if cell & bit or ncell & opp:
            #    continue

            maze.update(x, y, cell & ~bit)
            maze.update(nx, ny, ncell & ~opp)

    def generate(self, start: Tuple[int, int], end: Tuple[int, int]) -> Maze:
        #########
        # Added check to verify in can_fit_42() if end is in 42 stamp
        if not self.can_fit_42():
            raise ValueError(
                "Maze too small for 42 logo: requires at least 7x5"
            )
        #########
        #########
        # Added error check to verify if end is in 42 stamp
        if not self.inside(*start):
            raise ValueError("Invalid start position")
        if not self.inside(*end):
            raise ValueError("Invalid end position, it needs")
        #########
        maze = Maze(self.w, self.h)
        blocked = set()
        try:
            blocked = self._build_42_coords()
        except ValueError:
            blocked = set()
        #########
        # Added error check to verify if end is in 42 stamp
        if start in blocked:
            raise ValueError("Start coord are inside 42 stamp")
        if end in blocked:
            raise ValueError("End coord are inside 42 stamp")
        #########
        visited: Set[Tuple[int, int]] = set()
        stack: List[Tuple[int, int]] = [start]
        visited.add(start)
        while stack:
            x, y = stack[-1]
            neighbors = []
            for d, (dx, dy, *_) in DIRS.items():
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

#######################################
        # Solver step-by-step animation support (BFS)
    def iter_generation_steps(
        self, start: Tuple[int, int], end: Tuple[int, int]
    ):
        """Yield maze step-by-step for animation"""
        if not self.inside(*start) or not self.inside(*end):
            raise ValueError("Invalid start or end for animation")

        maze = Maze(self.w, self.h)
        blocked = self._build_42_coords() if self.can_fit_42() else set()

        if start in blocked or end in blocked:
            raise ValueError("Start or end inside 42 stamp")

        visited: Set[Tuple[int, int]] = set()
        stack: List[Tuple[int, int]] = [start]
        visited.add(start)

        parent: dict[Tuple[int, int], Tuple[Tuple[int, int], str]] = {}

        while stack:
            x, y = stack[-1]
            neighbors = []
            for d, (dx, dy, *_) in DIRS.items():
                nx, ny = x + dx, y + dy
                if not self.inside(nx, ny):
                    continue
                if (nx, ny) in visited or (nx, ny) in blocked:
                    continue
                neighbors.append((nx, ny, d))

            if not neighbors:
                stack.pop()
                # yield current maze state without updating path
                yield maze, list(self._reconstruct_path(parent, start, end))
                continue

            nx, ny, d = self.rng.choice(neighbors)
            self.break_wall(maze, x, y, d)
            visited.add((nx, ny))
            parent[(nx, ny)] = ((x, y), d)
            stack.append((nx, ny))

            # yield after every new cell
            yield maze, list(self._reconstruct_path(parent, start, end))

        if not self.perfect:
            self._add_loops(maze)

        self._apply_42(maze, blocked)
        yield maze, list(self._reconstruct_path(parent, start, end))

    def _reconstruct_path(
        self, parent: dict[Tuple[int, int], Tuple[Tuple[int, int], str]],
        start: Tuple[int, int], end: Tuple[int, int]
    ) -> List[str]:
        """Reconstruct path from start to end"""
        if end not in parent:
            return []
        path = []
        cur = end
        while cur != start:
            cur, d = parent[cur]
            path.append(d)
        return path[::-1]

####################################


def export_maze(maze, entry, exit, path, filename):
    with open(filename, "w") as f:
        for row in maze.grid:
            f.write("".join(format(cell, "X") for cell in row) + "\n")
        f.write("\n")
        f.write(f"{entry[0]},{entry[1]}\n")
        f.write(f"{exit[0]},{exit[1]}\n")
        f.write("".join(path) + "\n")
