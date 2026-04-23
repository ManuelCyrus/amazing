import sys

from config import parse_config
from maze_generator import generate_maze
from solve.solver import solve_maze
from maze_renderer import Maze_Renderer


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 teste.py config.txt")
        return 1

    # 1. ler config
    try:
        cfg = parse_config(sys.argv[1])
    except Exception as e:
        print(f"Config error: {e}")
        return 1

    # 2. gerar maze
    maze = generate_maze(cfg.width, cfg.height, cfg.seed)

    # 3. solver
    start = cfg.entry
    end = cfg.exit

    path = solve_maze(
        maze,
        start,
        end,
        cfg.width,
        cfg.height
    )

    # 4. renderer
    renderer = Maze_Renderer()

    renderer.create_maze(
        maze=maze,
        path=path,
        gen=None,   # ainda não tens animação generator
        cfg=cfg
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())