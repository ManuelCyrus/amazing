*This project has been created as part of the 42 curriculum by mkisala, jcrespo-*

# A-Maze-ing


## Description

A-Maze-ing project is maze generation and solving system developed as part of the 42 curriculum.
It's a Python maze generator that reads a text configuration file, builds a valid maze depending on the mode chosen (PERFECT or not), writes the result in the required hexadecimal wall format in an output file and displays the maze in the terminal in a ASCII visual interactive display.

A **perfect maze** has exactly one path between any two cells (no loops, no isolated regions). The maze generator supports only one algorithm, **Depth-First Search (DFS)**, and the solver support, **Breadth-First Search (BFS)**. Every maze generated is embeded with a visible **"42" logo** as a set of fully closed cells (the maze needs to be large enough to fit it). A solver computes the shortest path from entry to exit, this path can be shown or hidden in the visual display. Provides a method so that the generation logic can be reused later.

### Goals

The goals of this project are as follows:
- Parse input data to validate if a maze can be made
- Generate mazes using procedural algorithms
- Solve mazes using the shortest-path algorithms
- Provide an interactive ASCII visualization display
- Enforce obligatory constraints (borders, pathways, 42 stamp)
- The option to add various bonuses to the project (animation, ...)

## Instructions

### Installation

Using the provided Makefile:
```bash
# Install all dependencies needed
make install
```

### How to run


```bash
# Run the program manually
python3 a_maze_ing.py config.txt


# Or run through make
make run
```

- `a_maze_ing.py` is the main program file (name is mandatory).
- `config.txt` is the only argument (a plain-text configuration file).

```bash
# Debug the program
make debug

# Clean out
make clean

# Run linting checks (mypy + flake8)
make lint

# Run strict-lint checks
make lint-strict
```

### Error handling

If an error occurs, the program gives a message regarding what went wrong.

## Configuration File Structure

The configuration file uses one `KEY=VALUE` pair per line. The lines starting with `#` are comments and are ignored. Blank lines are ignored and unknown keys are rejected.

### Mandatory keys

| Key           | Description                                    |
|---------------|------------------------------------------------|
| `WIDTH`       | Maze width in number of cells                  |
| `HEIGHT`      | Maze height in number of cells                 |
| `ENTRY`       | Entry cell coordinates as `x,y`                |
| `EXIT`        | Exit cell coordinates as `x,y`                 |
| `OUTPUT_FILE` | Path to the output file                        |
| `PERFECT`     | Generate a perfect maze (`True` or `False`)    |

Mandatory keys full example:

```ini
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
```

### Optional key

| Key         | Description                                              |
|-------------|----------------------------------------------------------|
| `SEED`      | Integer seed for reproducible random generation          |

Optional key example:

```ini
SEED=42
```

## Output file format

In regards to the output file, each cell is represented by **one hexadecimal digit**. These encodes which walls are closed in the maze. The cells are stored row by row, one row per line.

### Bit mapping

| Bit | Direction |
|-----|-----------|
| 0 (LSB) | North |
| 1       | East  |
| 2       | South |
| 3       | West  |

A bit set to `1` signifies that it is a **closed** wall (present); while `0` means **open** wall (passage).

**Examples:** 
- 0xF = 1111 → all walls closed
- 0x5 = 0101 → South and North walls closed, East and West open

###  Output file structure

1. The hexadecimal maze — one row per line, each character is a hex digit for one cell.
2. An empty line.
3. The entry coordinates: `x, y`
4. The exit coordinates: `x, y`
5. Shortest path from entry to exit as a sequence of cardinal letters: `N`, `E`, `S`, `W`
6. All lines end with `\n`.

## Algorithm

### Validation of coordinates

- **No 3×3 Open Areas**: Constraint preventing open rectangular spaces larger than 2×2
- **Entry/Exit Validation**: Entry and exit points are outside all constraint zones


### Maze Generation Algorithm

Manuel, escreve aqui!!!!!! (Describe the algorythm and how it works)

**Depth-First Search (DFS)**

### Why this Algorithm

Manuel, escreve aqui!!!!!! (Describe why this algorythm for the generation)

### Maze Solver Algorithm

Manuel, escreve aqui!!!!!! (Describe the algorythm and how it works)

**Breadth-First Search (BFS)**

### Why this Algorithm

Manuel, escreve aqui!!!!!! (Describe why this algorythm for the solver, add anything you want)

- Explores level-by-level
- Guarantees the shortest path
- Animatable with the step-by-step frontier visualization

## Reusable Code

Manuel, escreve aqui!!!!!! (We need to take care of this man we forgot this, anything with a ??? needs to be replaced, you got this)

The reusable part of the project is `?????`, which is packaged as `????-1.0.0.tar.gz` and located at the root of the repository. This module can be installed independently via pip:

```bash
pip install ./???-1.0.0.tar.gz
```

## Visual representation

The program provides an **interactive terminal ASCII** instead of a graphical window,
it uses ASCII/Unicode characters to represent the maze, the walls are drawn with block characters (`█`). It uses colors to distinguish elements such as the entry cell (start) being one color, the Exit cell (end) being another color and the solution path being a different color. The ANSI color codes are what give these colors.

To represents the maze structure, each cell in the maze is stored as a hexadecimal digit (encoding which walls exist as mentioned before). The maze_renderer reads that information and converts it into visual walls and open spaces in the terminal. The “42 logo” stamp in the maze is displayed with a unique color and left untouched in the visualization.

And when using the step-by-step animation maze generation or solving, the renderer updates the display in real-time, showing the maze being carved or the solution being traced.

### Interactive Commands

Once the maze is displayed, the following commands are available:

| Command | Action |
|---------|--------|
| `0` | Quit the program |
| `1` | Regenerate new maze (applies current animation settings) |
| `2` | Toggle path solution display |
| `3` | Cycle through wall colors (3 options) |
| `4` | Toggle maze generation animation  |
| `5` | Toggle solver animation |
| `6` | Cycle through 42 logo colors (3 options) |
| `+` | Increase fps of animations (Faster animations) |
| `-` | Decrease fps of animations (Slower animations) |

---

### Color coding

| Color         | Meaning             |
|---------------|---------------------|
| White / Yellow / Blue | Maze walls (toggleable) |
| Green           | Entry cell          |
| Red            | Exit cell           |
| Briht cyan          | Shortest path cells |
| Yellow / Magenta / Pink          | "42" pattern cells (toggleable) |
| Grey / Dim  |  Visited cells during solver animation  |


## Team & Project Management

### Roles
This is a group project. All roles were divided by by mkisala and jcrespo-:

**jcrespo** = maze_renderer.py, config.py, a_maze_ing.py, config.txt, animation methods in solve/solver.py and solve/maze_generator.py

- Maze engine: Terminal rendering of maze, coloring, ASCII visualization, path and stamp display, user interaction (maze_renderer.py)
- Generation & Pathfinding logic (UI/UX side): Animation of maze generation & Animation of maze solver
- Configuration management (Read/write maze parameters, entry/exit coordinates, animation speed, color settings)
- Program orchestration (Main program loop, input handling, toggling features, regenerating maze, solving maze)
- Validation (runtime UI checks): Ensure renderer handles stamps, paths, walls correctly, including color, junctions and boundaries

**mkisala**: pyproject.toml, Makefile, solve/solver.py, solve/maze_generator.py, solve/__init__.py, requirements.txt

- Maze engine: Core representation of maze (Maze class) and wall data structures (solve/maze_generator.py)
- Generation logic & Pathfinding (core logic): Maze generation algorithm, wall breaking, loop addition, 42-stamp placement, BFS solver, movement validation, path reconstruction
- Validation (algorithmic): Ensure valid start/end coordinates, prevent paths through 42-stamp, maze bounds checking
- Packaging & environment setup: Python packaging (pyproject.toml), virtual environment, dependency management (requirements.txt), Makefile automation (run, debug, lint, clean)
- Module management: Ensure proper package structure and imports

### Anticipated planning and evolution

The work can be described in the following phases:

1. define orchestration of program
2. parse and validate the configuration file
3. implement terminal renderer and user interaction
4. implement maze generation
5. implement pathfinding and output export
6. implement maze generation and pathfinding animation
7. package the reusable code and finalize documentation

### What Worked Well

**Architecture**: separation of phases (parse, generation, solving, output print, rendering)
**Tests**: Error discovery, constraint validation
**Algorithm**: Algorithm was straight forward to add
**Animation**: Flexible step-by-step generation/solving granting visualization
**Type Safety**: Strict mypy checking
**Interactive Design**: Users can sap colors, toggle animations and control speed

### What coud be improved

**More Algorithm**: Make an option to swtch between generation and solving algorithms
**Performance**: Large mazes (>100×100) could benefit from parallel constraint checking
**Display flexibility**: Only ASCII supported
Manuel, escreve aqui!!!!!! (Describe anything else that could be added or improved)

## Resources

References used for the project:

- `Python documentation` : https://docs.python.org/3/
- `deque`: https://www.geeksforgeeks.org/python/deque-in-python/
- `Depth-First Search Maze` : https://en.wikipedia.org/wiki/Depth-first_search
- `typing`: https://docs.python.org/3/library/typing.html
- `pathlib`: https://docs.python.org/3/library/pathlib.html
- `Python packaging user guide`: https://packaging.python.org/
- `flake8` documentation: https://flake8.pycqa.org/
- `mypy` documentation: https://mypy.readthedocs.io/

AI usage in this project:

- AI was used to help structure documentation, review requirement coverage, and improve code organization.
- AI was also used to help refine type hints, error handling and explanations of algorithms.
- AI was used to locate and suggest solutions to really niche errors couldn't be found
