import random

# Bits das paredes
N, E, S, W = 1, 2, 4, 8

OPPOSITE = {
    N: S,
    S: N,
    E: W,
    W: E
}

DIRECTIONS = [
    (0, -1, N),
    (1, 0, E),
    (0, 1, S),
    (-1, 0, W)
]


def generate_maze(width: int, height: int, seed=None):
    if seed is not None:
        random.seed(seed)

    # cada célula começa com todas as paredes (1111 = 15)
    maze = [[15 for _ in range(width)] for _ in range(height)]
    visited = [[False] * width for _ in range(height)]

    def dfs(x, y):
        visited[y][x] = True

        dirs = DIRECTIONS[:]
        random.shuffle(dirs)

        for dx, dy, wall in dirs:
            nx, ny = x + dx, y + dy

            if 0 <= nx < width and 0 <= ny < height:
                if not visited[ny][nx]:

                    # remover parede entre células
                    maze[y][x] &= ~wall
                    maze[ny][nx] &= ~OPPOSITE[wall]

                    dfs(nx, ny)

    # começa no canto superior esquerdo
    dfs(0, 0)

    return maze