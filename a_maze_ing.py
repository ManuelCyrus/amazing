import sys
from maze_renderer import Maze_Renderer
from config import parse_config
from solve import MazeGenerator, MazeSolver
from solve.maze_generator import export_maze


def main() -> None:
    """
    Main function to run the maze generation,
    solving, exporting, and rendering.

    Steps:
    1. Parse the configuration file passed as a command-line argument.
    2. Generate a maze using the MazeGenerator class.
    3. Solve the generated maze using MazeSolver.
    4. Export the maze and solution path to a file.
    5. Render the maze and solution using Maze_Renderer.

    Raises:
        SystemExit: If the configuration file is missing, invalid,
                    or the program is interrupted.
    """
    if len(sys.argv) < 2:
        print("Use: python3 main.py config.txt")
        sys.exit(1)

    try:
        cfg_file = sys.argv[1]
        cfg = parse_config(cfg_file)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Initialize maze generator
    generator = MazeGenerator(
        width=cfg.width,
        height=cfg.height,
        seed=cfg.seed,
        perfect=cfg.perfect
    )

    # Generate the maze
    try:
        maze = generator.generate(start=cfg.entry, end=cfg.exit)
    except ValueError as e:
        print(f"Error generating maze: {e}")
        exit(1)

    # Solve the maze
    maze_solution = MazeSolver(maze)
    path = maze_solution.solve(cfg.entry, cfg.exit)

    # Export the maze and solution
    export_maze(maze, cfg.entry, cfg.exit, path, cfg.output_file)

    # Render the maze
    try:
        renderer = Maze_Renderer()
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
