import random

N, E, S, W = 1, 2, 4, 8

OPPOSITE = {N: S, S: N, E: W, W: E}

DIRECTIONS = [
    (0, -1, N),
    (1, 0, E),
    (0, 1, S),
    (-1, 0, W)
]


class MazeGenerator:
    def __init__(self, width: int, height: int, seed=None):
        self.width = width
        self.height = height
        self.seed = seed

    def generate_maze(self):
        if self.seed is not None:
            random.seed(self.seed)

        maze = [[N | E | S | W for _ in range(self.width)] for _ in range(self.height)]
        visited = [[False] * self.width for _ in range(self.height)]

        def dfs(x, y):
            visited[y][x] = True
            dirs = DIRECTIONS[:]
            random.shuffle(dirs)

            for dx, dy, wall in dirs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if not visited[ny][nx]:
                        maze[y][x] &= ~wall
                        maze[ny][nx] &= ~OPPOSITE[wall]
                        dfs(nx, ny)

        dfs(0, 0)

        maze[0][0] &= ~(N | W)
        maze[self.height - 1][self.width - 1] &= ~(S | E)

        return maze

__all__ = ["MazeGenerator", "N", "E", "S", "W", "DIRECTIONS"]