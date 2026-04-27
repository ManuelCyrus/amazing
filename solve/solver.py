from collections import deque
from typing import Tuple, List, Dict, Set, Iterator
from .maze_generator import Maze, DIRS


class MazeSolver:
    def __init__(self, maze: Maze):
        """
        Initialize the maze solver with a given maze.

        Args:
            maze (Maze): Maze object to solve.
        """
        self.maze = maze

    def can_go(self, x: int, y: int, d: str) -> bool:
        """
        Check if movement in a given direction is possible from a cell.

        Args:
            x (int): Current x-coordinate.
            y (int): Current y-coordinate.
            d (str): Direction ('N', 'E', 'S', 'W').

        Returns:
            bool: True if the move is allowed,
            False if blocked or out of bounds.
        """

        dx, dy, bit, _ = DIRS[d]
        nx, ny = x + dx, y + dy
        if not (0 <= nx < self.maze.w and 0 <= ny < self.maze.h):
            return False
        return (self.maze.cell(x, y) & bit) == 0

    def solve(self, start: Tuple[int, int], end: Tuple[int, int]) -> List[str]:
        """
        Solve the maze using BFS and return the path from start to end.

        Args:
            start (Tuple[int,int]): Coordinates of the maze entry.
            end (Tuple[int,int]): Coordinates of the maze exit.

        Returns:
            List[str]: Sequence of moves ('N', 'E', 'S', 'W')
            from start to end.
                       Empty list if no path exists.

        Raises:
            ValueError: If start or end coordinates are invalid.
        """

        if not (0 <= start[0] < self.maze.w and 0 <= start[1] < self.maze.h):
            raise ValueError("Invalid start")
        if not (0 <= end[0] < self.maze.w and 0 <= end[1] < self.maze.h):
            raise ValueError("Invalid end")
        queue = deque([start])
        visited = {start}
        parent: Dict[Tuple[int, int], Tuple[Tuple[int, int], str]] = {}
        while queue:
            x, y = queue.popleft()
            if (x, y) == end:
                break
            for d, (dx, dy, *_) in DIRS.items():
                if not self.can_go(x, y, d):
                    continue
                nx, ny = x + dx, y + dy
                nxt = (nx, ny)
                if nxt in visited:
                    continue
                visited.add(nxt)
                parent[nxt] = ((x, y), d)
                queue.append(nxt)
        if end not in parent:
            return []
        path = []
        cur = end
        while cur != start:
            cur, d = parent[cur]
            path.append(d)
        return path[::-1]

    def solve_bfs_steps(
        self,
        start: Tuple[int, int],
        end: Tuple[int, int],
        yield_every: int = 1
    ) -> Iterator[
            Tuple[Tuple[int, int],
                  Set[Tuple[int, int]],
                  Set[Tuple[int, int]],
                  List[str]]
                ]:
        """
        BFS solver generator that yields each step for animation purposes.

        Args:
            start (Tuple[int,int]): Maze entry coordinates.
            end (Tuple[int,int]): Maze exit coordinates.
            yield_every (int, optional): Yield state every N steps. Default 1.

        Yields:
            Tuple[
                Tuple[int,int],      # Current cell
                Set[Tuple[int,int]], # Visited cells
                Set[Tuple[int,int]], # Frontier cells
                List[str]            # Path from start to current
            ]

        Notes:
            - The generator yields the state after
            every `yield_every` BFS steps.
            - The final yield returns the full solution path.
        """

        # Initialize BFS queue with the starting cell
        queue = deque([start])
        # Set of visited cells to avoid revisiting
        visited: Set[Tuple[int, int]] = {start}
        # Frontier cells that are discovered but not yet fully explored
        frontier: Set[Tuple[int, int]] = {start}
        # Parent mapping to reconstruct path:
        # child -> (parent, direction taken)
        parent: Dict[Tuple[int, int], Tuple[Tuple[int, int], str]] = {}
        # Counter to determine when to yield for animation
        steps_counter = 0

        # Main BFS loop
        while queue:
            # Current cell is dequeued from the BFS queue
            x, y = queue.popleft()
            # Remove it from the frontier since we are now visiting it
            frontier.discard((x, y))

            # Stop BFS if we reached the end
            if (x, y) == end:
                break

            # Explore all possible directions from current cell
            for d, (dx, dy, *_) in DIRS.items():
                # Skip if movement in this direction is blocked by a wall
                if not self.can_go(x, y, d):
                    continue

                nx, ny = x + dx, y + dy
                nxt = (nx, ny)

                # Skip if this neighbor has already been visited
                if nxt in visited:
                    continue

                # Mark neighbor as visited
                visited.add(nxt)
                # Add neighbor to frontier for future exploration
                frontier.add(nxt)
                # Record parent and the direction taken to reach this neighbor
                parent[nxt] = ((x, y), d)
                # Enqueue neighbor for BFS exploration
                queue.append(nxt)

            # Increment steps counter and check if we should yield for anim
            steps_counter += 1
            if steps_counter % yield_every == 0:
                # Reconstruct the path from start to current cell
                path: List[str] = []
                cur = end
                if cur in parent:
                    while cur != start:
                        cur, d = parent[cur]
                        path.append(d)
                    # Reverse path to go from start to end
                    path = path[::-1]

                # Yield current BFS state for animation
                # Include current cell, visited set, frontier set, current path
                yield ((x, y), visited.copy(), frontier.copy(), path)

        # Final yield ensures animation finishes with the full solution path
        path: List[str] = []  # type: ignore[no-redef]
        cur = end
        if cur in parent:
            while cur != start:
                cur, d = parent[cur]
                path.append(d)
            path = path[::-1]

        # Yield the end state: all visited cells, empty frontier, full path
        yield (end, visited.copy(), set(), path)
