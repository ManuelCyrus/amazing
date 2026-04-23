from collections import deque

N, E, S, W = 1, 2, 4, 8


def bfs(maze, start, end):
    width, height = len(maze[0]), len(maze)

    queue = deque([start])
    visited = set([start])
    parent = {}

    moves = [(0,-1,N),(1,0,E),(0,1,S),(-1,0,W)]

    while queue:
        x,y = queue.popleft()

        yield {
            "current": (x,y),
            "visited": set(visited),
            "frontier": set(queue),
            "path": None
        }

        if (x,y) == end:
            break

        cell = maze[y][x]

        for dx,dy,wall in moves:
            if not (cell & wall):
                nx,ny = x+dx, y+dy

                if (0 <= nx < width and 0 <= ny < height):
                    if (nx,ny) not in visited:
                        visited.add((nx,ny))
                        parent[(nx,ny)] = (x,y)
                        queue.append((nx,ny))

    path = []
    cur = end

    while cur in parent:
        path.append(cur)
        cur = parent[cur]

    path.append(start)
    path.reverse()

    yield {
        "current": None,
        "visited": visited,
        "frontier": set(),
        "path": path
    }


def dfs(maze, start, end):
    width, height = len(maze[0]), len(maze)

    stack = [start]
    visited = set([start])
    parent = {}

    moves = [(0,-1,N),(1,0,E),(0,1,S),(-1,0,W)]

    while stack:
        x,y = stack.pop()

        yield {
            "current": (x,y),
            "visited": set(visited),
            "frontier": set(stack),
            "path": None
        }

        if (x,y) == end:
            break

        cell = maze[y][x]

        for dx,dy,wall in moves:
            if not (cell & wall):
                nx,ny = x+dx, y+dy

                if (0 <= nx < width and 0 <= ny < height):
                    if (nx,ny) not in visited:
                        visited.add((nx,ny))
                        parent[(nx,ny)] = (x,y)
                        stack.append((nx,ny))

    path = []
    cur = end

    while cur in parent:
        path.append(cur)
        cur = parent[cur]

    path.append(start)
    path.reverse()

    yield {
        "current": None,
        "visited": visited,
        "frontier": set(),
        "path": path
    }


def solve_maze_anim(maze, start, end, algorithm="bfs"):
    if algorithm == "dfs":
        return dfs(maze, start, end)
    return bfs(maze, start, end)