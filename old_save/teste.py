from maze_renderer import Maze_Renderer
from config import parse_config
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

    try:
        cfg_file = sys.argv[1]
        # Exemplo de leitura simples. Ajuste conforme seu config.py
        cfg = parse_config(cfg_file)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    generator = MazeGenerator(cfg.width, cfg.height, seed=cfg.seed)
    maze = generator.generate_maze()
    path = solve_maze(maze, cfg.entry, cfg.exit)

    try:
        renderer = Maze_Renderer()
        # Renderiza o labirinto com o caminho
        renderer.create_maze(maze, path, generator, cfg)
    except (KeyboardInterrupt, ValueError) as e:
        if isinstance(e, KeyboardInterrupt):
            print("\nProgram interrupted by user.", file=sys.stderr)
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
