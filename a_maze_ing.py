import sys
from config import parse_config
from maze_renderer import Maze_Renderer


def main(argv: list[str]) -> int:

    if len(argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        return 2

    try:
        config = parse_config(argv[1])
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        return 1

    # Input has been parsed, now we do maze
    #
    #
    #

    maze = ... # generate the maze structure
    path = ... # solve the maze for path

    # Renderer of the maze
    try:
        renderer = Maze_Renderer()
        renderer.create_maze(maze=maze, path= path)
    except (KeyboardInterrupt, ValueError) as e:
        if isinstance(e, KeyboardInterrupt):
            print("\nProgram interrupted by user.", file=sys.stderr)
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    main()
