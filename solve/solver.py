from collections import deque

# direções (compatível com o teu maze_generator)
N, E, S, W = 1, 2, 4, 8


def solve_maze(maze, start, end, width, height):
    queue = deque([start])
    visited = set([start])
    parent = {}

    while queue:
        x, y = queue.popleft()

        if (x, y) == end:
            break

        cell = maze[y][x]

        # NORTE
        if not (cell & N):
            nx, ny = x, y - 1
            if 0 <= nx < width and 0 <= ny < height:
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    parent[(nx, ny)] = (x, y)
                    queue.append((nx, ny))

        # ESTE
        if not (cell & E):
            nx, ny = x + 1, y
            if 0 <= nx < width and 0 <= ny < height:
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    parent[(nx, ny)] = (x, y)
                    queue.append((nx, ny))

        # SUL
        if not (cell & S):
            nx, ny = x, y + 1
            if 0 <= nx < width and 0 <= ny < height:
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    parent[(nx, ny)] = (x, y)
                    queue.append((nx, ny))

        # OESTE
        if not (cell & W):
            nx, ny = x - 1, y
            if 0 <= nx < width and 0 <= ny < height:
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    parent[(nx, ny)] = (x, y)
                    queue.append((nx, ny))

    # reconstruir caminho (shortest path)
    path = []
    cur = end

    while cur in parent:
        path.append(cur)
        cur = parent[cur]

    path.append(start)
    path.reverse()

    return path