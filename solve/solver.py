from collections import deque
from typing import Tuple, List, Dict
from .maze_generator import Maze, DIRS

class MazeSolver:
    def __init__(self, maze: Maze):
        self.maze = maze

    def can_go(self, x: int, y: int, d: str) -> bool:
        dx, dy, bit, _ = DIRS[d]
        nx, ny = x + dx, y + dy
        if not (0 <= nx < self.maze.w and 0 <= ny < self.maze.h):
            return False
        return (self.maze.cell(x, y) & bit) == 0

    def solve(self, start: Tuple[int, int], end: Tuple[int, int]) -> List[str]:
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
            for d, (dx, dy, *_ ) in DIRS.items():
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
