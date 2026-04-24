import sys
from maze_renderer import Maze_Renderer
from config import parse_config
from solve import MazeGenerator, MazeSolver
from solve.maze_generator import export_maze


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

    generator = MazeGenerator(
        width=cfg.width,
        height=cfg.height,
        seed=cfg.seed,
        perfect=cfg.perfect
    )
    #    gen = MazeGenerator(
    #       width=cfg.width,
    #       height=cfg.height,
    #       seed=cfg.seed,
    #       perfect=cfg.perfect
    # )

    maze = generator.generate(start=cfg.entry, end=cfg.exit)
    # This is supposed to be the generate maze structure.
    # You need to send to generate_maze the entry=cfg.entry and exit=cfg.exit
    # maze = generator.generate_maze(entry=cfg.entry, exit=cfg.exit)

    maze_solution = MazeSolver(maze)
    path = maze_solution.solve(cfg.entry, cfg.exit)
    # This is supposed to be the solver of the maze,
    # not sure where the solver is gonna be in.
    # You need to send to maze, the entry=cfg.entry and exit=cfg.exit
    # path = gen.solve(maze, cfg.entry, cfg.exit)

    export_maze(maze, cfg.entry, cfg.exit, path, cfg.output_file)

    try:
        renderer = Maze_Renderer()
    # This is the renderer it's not suppost to solve anything,
    # just print out stuff and animation.
    # I use maze, path, generator and cfg
        renderer.create_maze(maze, path, generator, cfg, maze_solution)
    except (KeyboardInterrupt, ValueError) as e:
        if isinstance(e, KeyboardInterrupt):
            print("\nProgram interrupted by user.", file=sys.stderr)
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("interrupt")
