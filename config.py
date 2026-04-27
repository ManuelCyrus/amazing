from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Config:
    """
    Configuration for maze generation and solving.

    Attributes:
        width (int): Width of the maze.
        height (int): Height of the maze.
        entry (tuple[int, int]): Entry coordinates (x, y).
        exit (tuple[int, int]): Exit coordinates (x, y).
        output_file (str): Path to export the maze solution.
        perfect (bool): Whether the maze should be perfect (no loops).
        seed (Optional[int]): Random seed for maze generation.
    """
    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: Optional[int] = None


def _verify_coord(value: str) -> tuple[int, int]:
    """
    Convert a string "x,y" into a tuple of integers.

    Args:
        value (str): Coordinate string in the format "x,y".

    Returns:
        Tuple[int, int]: Parsed coordinate.

    Raises:
        ValueError: If the input is not properly formatted or not integers.
    """
    try:
        coord = value.split(",")
        if len(coord) != 2:
            raise ValueError
        x, y = map(int, coord)
        return (x, y)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid coordinate format (expected x,y): {value}")


def _verify_bool(value: str) -> bool:
    """
    Convert a string to boolean.

    Args:
        value (str): String value, expected "true" or "false".

    Returns:
        bool: Converted boolean value.

    Raises:
        ValueError: If the string is not "true" or "false".
    """
    val = value.strip().lower()
    if val == "true":
        return True
    if val == "false":
        return False
    raise ValueError(f"Invalid boolean value: {value}")


def _verify_optional_int(value: Optional[str]) -> Optional[int]:
    """
    Convert a string to an optional integer.

    Args:
        value (Optional[str]): String representing an integer or None.

    Returns:
        Optional[int]: Integer value or None.

    Raises:
        ValueError: If the string is not a valid integer.
    """
    if value is None:
        return None
    text = value.strip()
    if not text or text.lower() == "none":
        return None
    try:
        return int(text)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid integer value: {value}")


def parse_config(path: str) -> Config:

    """
    Parse a configuration file and return a Config object.

    Args:
        path (str): Path to the configuration file.

    Returns:
        Config: Parsed configuration object.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If any configuration value is invalid or missing.
    """

    required = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"]
    data_dict: dict[str, str] = {}

    pathway = Path(path)
    if not pathway.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    # Parse key=value lines
    for line in pathway.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if "#" in line:
            line = line.split("#", 1)[0].strip()

        if "=" not in line:
            raise ValueError(f"Invalid line (expected KEY=VALUE): {line}")

        key, value = line.split("=", 1)
        data_dict[key.strip().upper()] = value.strip()

    # Check for missing mandatory keys
    missing = [k for k in required if k not in data_dict]
    if missing:
        raise ValueError(f"Missing mandatory keys: {', '.join(missing)}")

    # Validate width and height
    try:
        width = int(data_dict["WIDTH"])
        height = int(data_dict["HEIGHT"])
        if width <= 0 or height <= 0:
            raise ValueError("WIDTH and HEIGHT must be positive integers.")

        if width <= 9 or height <= 9:  # to change
            print("Warning: Maze too small for 42 pattern")
    except ValueError as e:
        raise ValueError(f"Configuration error: {e}")

    # Validate entry and exit coordinates
    try:
        entry_coord = _verify_coord(data_dict["ENTRY"])
        exit_coord = _verify_coord(data_dict["EXIT"])

        for name, (x, y) in [("ENTRY", entry_coord), ("EXIT", exit_coord)]:
            if not (0 <= x < width and 0 <= y < height):
                raise ValueError(
                    f"{name} {x, y} is outside maze bounds ({width}x{height})."
                )
        if entry_coord == exit_coord:
            raise ValueError("ENTRY and EXIT coordinates must be different.")
    except ValueError as e:
        raise ValueError(f"Configuration error: {e}")

    # Validate output file path
    try:
        output_path = data_dict["OUTPUT_FILE"]
        if not output_path.strip():
            raise ValueError("OUTPUT_FILE parameter cannot be empty.")
        out_p = Path(output_path)
        if not out_p.parent.exists():
            raise ValueError(
                f"Directory for output file does not exist: {out_p.parent}"
            )
    except ValueError as e:
        raise ValueError(f"Configuration error: {e}")

    # Validate perfect boolean
    try:
        perfect = _verify_bool(data_dict["PERFECT"])
    except ValueError as e:
        raise ValueError(f"Configuration error: {e}")

    # Validate seed
    try:
        seed_raw = data_dict.get("SEED")
        if seed_raw is None:
            seed = 42
        else:
            seed = _verify_optional_int(seed_raw)  # type: ignore[assignment]
    except ValueError as e:
        raise ValueError(f"Configuration error: {e}")

    return Config(
            width=width,
            height=height,
            entry=entry_coord,
            exit=exit_coord,
            output_file=output_path,
            perfect=perfect,

            seed=seed,
    )
