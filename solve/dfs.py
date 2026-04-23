import random

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


def dfs_generate(maze, x, y, visited, width, height):
    visited[y][x] = True

    dirs = DIRECTIONS[:]
    random.shuffle(dirs)

    for dx, dy, wall in dirs:
        nx, ny = x + dx, y + dy

        if 0 <= nx < width and 0 <= ny < height:
            if not visited[ny][nx]:

                # abrir caminho
                maze[y][x] &= ~wall
                maze[ny][nx] &= ~OPPOSITE[wall]

                dfs_generate(maze, nx, ny, visited, width, height)