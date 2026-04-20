import sys
from config import parse_config


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


if __name__ == "__main__":
    main()
