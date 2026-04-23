from maze_renderer import Maze_Renderer
from config import Config
from maze_generator import MazeGenerator, N, E, S, W, DIRECTIONS
import sys

def solve_maze(maze, start, end):
    """Resolve o labirinto e retorna uma lista de direções do entry até exit."""
    width, height = len(maze[0]), len(maze)
    visited = [[False] * width for _ in range(height)]
    path = []

    DIR_MAP = {N: 'N', S: 'S', E: 'E', W: 'W'}

    def dfs(x, y):
        if (x, y) == end:
            return True
        visited[y][x] = True
        for dx, dy, wall in DIRECTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                # Sem parede na direção
                if maze[y][x] & wall == 0 and not visited[ny][nx]:
                    path.append(DIR_MAP[wall])
                    if dfs(nx, ny):
                        return True
                    path.pop()
        return False

    dfs(*start)
    return path

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 main.py config.txt")
        sys.exit(1)

    cfg_file = sys.argv[1]
    # Exemplo de leitura simples. Ajuste conforme seu config.py
    cfg = Config(20, 10, (0, 0), (19, 9), "output.txt", perfect=True)

    renderer = Maze_Renderer()
    generator = MazeGenerator(cfg.width, cfg.height, seed=getattr(cfg, "seed", None))
    maze = generator.generate_maze()
    path = solve_maze(maze, cfg.entry, cfg.exit)

    # Renderiza o labirinto com o caminho
    renderer.create_maze(maze, path, generator, cfg)

if __name__ == "__main__":
    main()