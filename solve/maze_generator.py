import random
from typing import Optional, List, Tuple, Set, Generator

N, E, S, W = 1, 2, 4, 8

DIRS = {
    "N": (0, -1, N, S),
    "E": (1, 0, E, W),
    "S": (0, 1, S, N),
    "W": (-1, 0, W, E),
}


class Maze:
    """Represents a 2D maze grid with walls
    and optional 42-logo coordinates."""

    def __init__(self, w: int, h: int):
        """
        Initialize a maze grid with all walls intact.

        Args:
            w (int): Width of the maze.
            h (int): Height of the maze.
        """

        self.w = w
        self.h = h
        self.grid: List[List[int]] = [
            [15 for _ in range(w)] for _ in range(h)
        ]
        # Coordinates of 42-logo cells (for rendering)
        self.stamp42: set[Tuple[int, int]] = set()

    def cell(self, x: int, y: int) -> int:
        """Return the value of the cell at coordinates (x, y)."""
        return self.grid[y][x]

    def update(self, x: int, y: int, value: int) -> None:
        """Set the value of the cell at coordinates (x, y)."""
        self.grid[y][x] = value


class MazeGenerator:
    """Generates a 2D maze with optional 42-logo and loops."""
    def __init__(
            self, width: int,
            height: int,
            seed: Optional[int] = None,
            perfect: bool = True
            ):
        """
        Initialize the maze generator.

        Args:
            width (int): Width of the maze.
            height (int): Height of the maze.
            seed (Optional[int]): Random seed for reproducibility.
            perfect (bool): If True, maze will have no loops.
        """

        self.w = width
        self.h = height
        self.rng = random.Random(seed)
        self.perfect = perfect
        self.current_seed: int | None = seed

    def inside(self, x: int, y: int) -> bool:
        """Check if (x, y) is inside maze bounds."""
        return 0 <= x < self.w and 0 <= y < self.h
# open between 2 cell

    def break_wall(self, maze: Maze, x: int, y: int, d: str) -> None:
        """Remove wall in direction d from cell (x, y)."""
        dx, dy, bit, opp = DIRS[d]
        nx, ny = x + dx, y + dy
        if not self.inside(nx, ny):
            return
        maze.update(x, y, maze.cell(x, y) & ~bit)
        maze.update(nx, ny, maze.cell(nx, ny) & ~opp)

    def _get_42_pattern(self) -> List[str]:
        """Return a 42-logo pattern depending on maze size."""
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
        """Compute maze coordinates for the 42-logo."""
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
        """Check if maze is large enough to place the 42-logo."""
        pattern = self._get_42_pattern()
        ph = len(pattern)
        pw = len(pattern[0])
        return self.w >= pw and self.h >= ph

    def _apply_42(self, maze: Maze, coords: Set[Tuple[int, int]]) -> None:
        for x, y in coords:
            maze.stamp42 = coords
        """Apply 42-logo coordinates to the maze for rendering."""

    def _add_loops(self, maze: Maze) -> None:
        """Add random loops in the maze while avoiding the 42-logo."""
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
            # if cell & bit or ncell & opp:
            #    continue

            maze.update(x, y, cell & ~bit)
            maze.update(nx, ny, ncell & ~opp)

    def generate(self, start: Tuple[int, int], end: Tuple[int, int]) -> Maze:
        """
        Generate a new maze.

        Args:
            start (Tuple[int,int]): Starting coordinates.
            end (Tuple[int,int]): Ending coordinates.

        Returns:
            Maze: Generated maze with optional 42-logo and loops.

        Raises:
            ValueError: If maze too small or start/end in logo area.
        """
        # Added check to verify in can_fit_42() if end is in 42 stamp
        if not self.can_fit_42():
            raise ValueError(
                "Maze too small for 42 logo: requires at least 7x5"
            )
        # Added error check to verify if end is in 42 stamp
        if not self.inside(*start):
            raise ValueError("Invalid start position")
        if not self.inside(*end):
            raise ValueError("Invalid end position")

        maze = Maze(self.w, self.h)
        blocked = set()
        try:
            blocked = self._build_42_coords()
        except ValueError:
            blocked = set()

        # Added error check to verify if end is in 42 stamp
        if start in blocked:
            raise ValueError("Start coord are inside 42 stamp")
        if end in blocked:
            raise ValueError("End coord are inside 42 stamp")

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
        self._apply_42(maze, blocked)
        if not self.perfect:
            self._add_loops(maze)
        return maze

    def iter_generation_steps(
        self, start: Tuple[int, int], end: Tuple[int, int]
    ) -> Generator[Tuple[Maze, List[str]], None, None]:

        """
        Generate maze states step-by-step for animation purposes.

        This is a depth-first maze generation iterator that yields the maze
        and the current solution path after each step. It respects the 42-logo
        area and ensures start/end are outside the blocked cells.

        Args:
            start (Tuple[int,int]): Coordinates of the maze entry point.
            end (Tuple[int,int]): Coordinates of the maze exit point.

        Yields:
            Tuple[Maze, List[str]]: A tuple containing:
                - Maze: The current state of the maze grid.
                - List[str]: Current path from start to end (reconstructed).

        Raises:
            ValueError: If start or end coordinates are out of bounds or
                        overlap with the 42-logo cells.
        """

        # Ensure start and end are within maze bounds
        if not self.inside(*start) or not self.inside(*end):
            raise ValueError("Invalid start or end for animation")

        # Create an empty maze grid
        maze = Maze(self.w, self.h)
        # Determine blocked cells from the 42-logo if the maze is large enough
        blocked = self._build_42_coords() if self.can_fit_42() else set()

        # Make sure start/end are not inside the blocked 42-logo area
        if start in blocked or end in blocked:
            raise ValueError("Start or end inside 42 stamp")

        # Track visited cells for depth-first generation
        visited: Set[Tuple[int, int]] = set()
        stack: List[Tuple[int, int]] = [start]
        visited.add(start)

        # Track parent relationships for path reconstruction
        parent: dict[Tuple[int, int], Tuple[Tuple[int, int], str]] = {}

        # Main DFS loop
        while stack:
            x, y = stack[-1]  # Current cell is top of the stack
            neighbors = []

            # Find unvisited, in-bounds, non-blocked neighbors
            for d, (dx, dy, *_) in DIRS.items():
                nx, ny = x + dx, y + dy
                if not self.inside(nx, ny):
                    continue
                if (nx, ny) in visited or (nx, ny) in blocked:
                    continue
                neighbors.append((nx, ny, d))

            if not neighbors:
                # Dead-end reached; backtrack
                stack.pop()
                # Yield current maze and reconstructed path without moving
                yield maze, list(self._reconstruct_path(parent, start, end))
                continue

            # Randomly select a neighbor to carve
            nx, ny, d = self.rng.choice(neighbors)
            self.break_wall(maze, x, y, d)
            # Carve wall between current and neighbor
            visited.add((nx, ny))
            # Mark neighbor as visited
            parent[(nx, ny)] = ((x, y), d)
            # Record parent for path reconstruction
            stack.append((nx, ny))
            # Add neighbor to DFS stack

            # Yield maze and path after carving each new cell
            yield maze, list(self._reconstruct_path(parent, start, end))

        # Add loops to maze if not perfect (optional)
        if not self.perfect:
            self._add_loops(maze)

        # Apply 42-logo coordinates at the end
        self._apply_42(maze, blocked)
        # Yield final maze and path
        yield maze, list(self._reconstruct_path(parent, start, end))

    def _reconstruct_path(
        self, parent: dict[Tuple[int, int], Tuple[Tuple[int, int], str]],
        start: Tuple[int, int], end: Tuple[int, int]
    ) -> List[str]:
        """
        Reconstruct the path from start to end using parent pointers.

        Args:
            parent (Dict[Tuple[int,int], Tuple[Tuple[int,int], str]]):
                Mapping of child cell to its parent cell and the move taken.
            start (Tuple[int,int]): Start coordinates.
            end (Tuple[int,int]): End coordinates.

        Returns:
            List[str]: Ordered sequence of moves ('N', 'E', 'S', 'W') from
                    start to end. Returns an empty list if no path exists.
        """

        #  If the end cell was never visited, no path exists
        if end not in parent:
            return []
        path = []  # List to store moves from start to end
        cur = end  # Start reconstructing from the end

        # Walk backwards from end to start using parent pointers
        while cur != start:
            # Get parent cell and move used to reach current
            cur, d = parent[cur]
            # Append move to path
            path.append(d)

        # Reverse the path to go from start -> end
        return path[::-1]


def export_maze(maze, entry, exit, path, filename) -> None:
    """
    Export the maze, start/end positions, and solution path to a file.

    The maze grid is written in hexadecimal format, followed by a blank line,
    the entry and exit coordinates, and finally the solution path as a string.

    Args:
        maze (Maze): The maze object containing the grid to export.
        entry (Tuple[int,int]): Coordinates of the start cell.
        exit (Tuple[int,int]): Coordinates of the end cell.
        path (List[str]): List of moves ('N', 'E', 'S', 'W') representing
                          the solution path.
        filename (str): Output file path.

    Returns:
        None
    """
    with open(filename, "w") as f:
        for row in maze.grid:
            f.write("".join(format(cell, "X") for cell in row) + "\n")
        # Blank line before coordinates
        f.write("\n")
        # Entry and exit coordinates
        f.write(f"{entry[0]},{entry[1]}\n")
        f.write(f"{exit[0]},{exit[1]}\n")
        # Solution path as a single string
        f.write("".join(path) + "\n")
