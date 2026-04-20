from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Config:

    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: Optional[int] = None


def _verify_coord(value: str) -> tuple[int, int]:
    try:
        coord = value.split(",")
        if len(coord) != 2:
            raise ValueError
        x, y = map(int, coord)
        return (x, y)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid coordinate format (expected x,y): {value}")


def _verify_bool(value: str) -> bool:
    val = value.strip().lower()
    if val == "true":
        return True
    if val == "false":
        return False
    raise ValueError(f"Invalid boolean value: {value}")


def _verify_optional_int(value: Optional[str]) -> Optional[int]:

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

    required = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"]
    data_dict: dict[str, str] = {}

    pathway = Path(path)
    if not pathway.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

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

    missing = [k for k in required if k not in data_dict]
    if missing:
        raise ValueError(f"Missing mandatory keys: {', '.join(missing)}")

    # VALIDATE HEIGHT AND WIDTH
    try:
        width = int(data_dict["WIDTH"])
        height = int(data_dict["HEIGHT"])
        if width <= 0 or height <= 0:
            raise ValueError("WIDTH and HEIGHT must be positive integers.")

        if width <= 9 or height <= 9:  # to change
            print("Warning: Maze too small for 42 pattern")
    except ValueError as e:
        raise ValueError(f"Configuration error: {e}")

    # VALIDATE ENTRY_COORD AND WIDTH_COORD
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

    # VALIDATE OUTPUT AND PARENT DIRECTORY
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

    # VALIDATE PERFECT
    try:
        perfect = _verify_bool(data_dict["PERFECT"])
    except ValueError as e:
        raise ValueError(f"Configuration error: {e}")

    # VALIDATE_SEED
    try:
        seed_raw = data_dict.get("SEED")
        if seed_raw is None:
            seed = 42
        else:
            seed = _verify_optional_int(seed_raw)
    except ValueError as e:
        raise ValueError(f"Configuration error: {e}")

    return Config(
            width=width,
            height=height,
            entry=entry_coord,
            exit=exit_coord,
            output_file=data_dict["OUTPUT_FILE"],
            perfect=perfect,

            seed=seed,
    )
