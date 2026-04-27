import signal
import sys
import time
import random
from solve import MazeGenerator, Maze, MazeSolver
from config import Config
from solve.maze_generator import export_maze


class Maze_Renderer:
    """
    Renders a maze in the terminal with ASCII characters, ANSI colors,
    and optional animations for maze generation and solution path.

    Attributes:
        show_path (bool): Whether to display the solution path.
        animate_solver (bool): Whether to animate the maze solver.
        animate_generation (bool): Whether to animate maze generation.
        wall_colors (list[str]): ANSI color codes for maze walls.
        color_index (int): Current index in wall_colors.
        wall_color (str): Current wall color.
        animation_speed (float): Delay in seconds between animation frames.
        stamp_colors (list[str]): ANSI color codes for the 42 stamp.
        stamp_c_i (int): Current index in stamp_colors.
        stamp_color (str): Current color for the 42 stamp.
    """

    def __init__(self) -> None:
        """
        Initialize the Maze_Renderer with default colors, animation speed,
        and signal handlers to handle clean suspension and termination.
        """

        signal.signal(signal.SIGTSTP, self._handle_suspend)
        signal.signal(signal.SIGQUIT, self._handle_suspend)
        signal.signal(signal.SIGHUP, self._handle_suspend)
        signal.signal(signal.SIGTERM, self._handle_suspend)
        self.show_path: bool = True
        self.animate_solver: bool = False
        self.animate_generation: bool = False

        self.wall_colors: list[str] = ["\033[0m", "\033[33m", "\033[34m"]
        self.color_index: int = 0
        self.wall_color: str = self.wall_colors[0]
        self.animation_speed: float = 0.03

        self.stamp_colors: list[str] = ["\033[93m", "\033[95m", "\033[91m"]
        # yellow, magenta, pink
        self.stamp_c_i: int = 0
        self.stamp_color: str = self.stamp_colors[0]

    def _handle_suspend(
        self, signum: int, frame: object | None
    ) -> None:
        """
        Handle signals for clean suspension or termination.

        Args:
            signum (int): Signal number.
            frame (Optional[object]): Current stack frame.

        Raises:
            KeyboardInterrupt: Always raised to stop program execution cleanly.
        """
        raise KeyboardInterrupt

    def _build_maze(
        self,
        maze: Maze,
        cfg: Config,
        path: list[str],
        visited: set[tuple[int, int]] | None = None,
        frontier: set[tuple[int, int]] | None = None,
        current: tuple[int, int] | None = None,
    ) -> None:
        """
        Render the maze in the terminal using ASCII characters and ANSI colors.

        Args:
            - maze (Maze): Maze object (grid and stamp42 coordinates).
            - cfg (Config): Configuration (entry and exit positions).
            - path (List[str]): List of directions (solution path).
            - visited (Optional[Set[Tuple[int,int]]]): Cells visited by solver.
            - frontier (Optional[Set[Tuple[int,int]]]): Cells in the solver
            frontier.
            - current (Optional[Tuple[int,int]]): Current cell for animation
            cursor.
        """

        WALL_COLOR = self.wall_color  # Set by user interaction
        ENTRY_COLOR = "\033[32m"      # Green
        EXIT_COLOR = "\033[31m"       # Red
        PATH_COLOR = "\033[96m"       # Bright cyan for solution path
        RESET = "\033[0m"             # reset color to default
        BLOCK = "█"

        # Convert solution path directions
        # to actual cell coordinates for coloring
        path_coords = set()
        path_connectors: set[tuple[int, int, str]] = set()
        stamp_coords: set[tuple[int, int]] = getattr(
            maze, "stamp42", set()
        )
        has_stamp = bool(stamp_coords)

        if self.show_path and path:
            # Include entry in path
            x, y = cfg.entry
            path_coords.add((x, y))
            for direction in path:
                # Transform maze coordinates to grid coordinates
                # for ASCII rendering
                gx, gy = 2 * x + 1, 2 * y + 1
                if direction == 'N':
                    # Vertical connector
                    path_connectors.add((gy - 1, gx, "V"))
                    y -= 1
                elif direction == 'S':
                    path_connectors.add((gy + 1, gx, "V"))
                    y += 1
                elif direction == 'E':
                    # Horizontal connector
                    path_connectors.add((gy, gx + 1, "H"))
                    x += 1
                elif direction == 'W':
                    path_connectors.add((gy, gx - 1, "H"))
                    x -= 1
                else:
                    # Skip invalid directions
                    continue
                path_coords.add((x, y))
            # Ensure exit is included in path
            path_coords.add(cfg.exit)

        # Define set of characters that are considered walls
        wall_chars = {
            "─", "│", "┌", "┐",
            "└", "┘", "├", "┤",
            "┬", "┴", "┼",
        }

        # Helper to select correct junction character based
        # on surrounding walls
        def _junction_char(
            up: bool, down: bool, left: bool, right: bool
        ) -> str:
            key = (up, down, left, right)
            mapping = {
                (False, False, False, False): " ",
                (True, True, False, False): "│",
                (False, False, True, True): "─",
                (False, True, False, True): "┌",
                (False, True, True, False): "┐",
                (True, False, False, True): "└",
                (True, False, True, False): "┘",
                (True, True, False, True): "├",
                (True, True, True, False): "┤",
                (False, True, True, True): "┬",
                (True, False, True, True): "┴",
                (True, True, True, True): "┼",
            }
            return mapping.get(key, " ")

        # Grid dimensions in ASCII terms (cells and walls interleaved)
        rows = len(maze.grid)
        cols = len(maze.grid[0]) if rows > 0 else 0
        grid_h = rows * 2 + 1
        grid_w = cols * 2 + 1
        # Initialize empty ASCII grid
        grid: list[list[str]] = [
            [" " for _ in range(grid_w)] for _ in range(grid_h)
        ]

        # Populate grid with:
        # walls, cells, path, stamps, visited/frontier highlights
        for y, row in enumerate(maze.grid):
            for x, cell_value in enumerate(row):
                # 1) Determine cell type and center character
                if (x, y) == cfg.entry:
                    center_char = f"{ENTRY_COLOR}{BLOCK}{RESET}"
                elif (x, y) == cfg.exit:
                    center_char = f"{EXIT_COLOR}{BLOCK}{RESET}"
                elif has_stamp and (x, y) in stamp_coords:
                    center_char = f"{self.stamp_color}{BLOCK}{RESET}"
                elif current and (x, y) == current:
                    # Current solver position
                    center_char = "\033[95m█\033[0m"
                elif frontier and (x, y) in frontier:
                    # Solver frontier
                    center_char = "\033[94m█\033[0m"
                elif visited and (x, y) in visited:
                    # Visited cells
                    center_char = "\033[90m█\033[0m"
                elif (x, y) in path_coords:
                    # Solution path
                    center_char = f"{PATH_COLOR}{BLOCK}{RESET}"
                else:
                    # Empty cell
                    center_char = " "

                grid[2 * y + 1][2 * x + 1] = center_char

                # Determine which walls exist using bitmask
                n_wall_exists = bool(cell_value & 1)
                e_wall_exists = bool(cell_value & 2)
                s_wall_exists = bool(cell_value & 4)
                w_wall_exists = bool(cell_value & 8)

                # Draw walls in ASCII grid
                if n_wall_exists:
                    grid[2 * y][2 * x + 1] = "─"
                if s_wall_exists:
                    grid[2 * y + 2][2 * x + 1] = "─"
                if w_wall_exists:
                    grid[2 * y + 1][2 * x] = "│"
                if e_wall_exists:
                    grid[2 * y + 1][2 * x + 2] = "│"

        # Connect path cells visually so path appears continuous
        for gy, gx, orient in path_connectors:
            if 0 <= gy < grid_h and 0 <= gx < grid_w:
                if grid[gy][gx] == " ":
                    grid[gy][gx] = orient

        # Track central path cell positions for junction adjustments
        path_center_grid = {
            (2 * y + 1, 2 * x + 1) for (x, y) in path_coords
        }

        # Resolve junctions for continuous line appearance
        for gy in range(0, grid_h, 2):
            for gx in range(0, grid_w, 2):
                up = gy > 0 and grid[gy - 1][gx] == "│"
                down = gy < grid_h - 1 and grid[gy + 1][gx] == "│"
                left = gx > 0 and grid[gy][gx - 1] == "─"
                right = gx < grid_w - 1 and grid[gy][gx + 1] == "─"
                grid[gy][gx] = _junction_char(up, down, left, right)

        # Print the grid to terminal with colors
        right_edge_chars = {"─", "┌", "└", "├", "┬", "┴", "┼"}
        for gy, grid_row in enumerate(grid):
            line = ""
            for gx, ch in enumerate(grid_row):
                if ch in wall_chars:
                    line += f"{WALL_COLOR}{ch}{RESET}"
                elif ch == "H":
                    line += f"{PATH_COLOR}{BLOCK}{RESET}"
                elif ch == "V":
                    line += f"{PATH_COLOR}{BLOCK}{RESET}"
                else:
                    line += ch

                # Add spacing or connecting block to the right
                if gx == grid_w - 1:
                    continue
                next_ch = grid_row[gx + 1]
                if ch in right_edge_chars:
                    line += f"{WALL_COLOR}─{RESET}"
                elif ch == "H":
                    line += f"{PATH_COLOR}{BLOCK}{RESET}"
                elif (gy, gx) in path_center_grid and (
                    next_ch == "H" or (gy, gx + 1) in path_center_grid
                ):
                    line += f"{PATH_COLOR}{BLOCK}{RESET}"
                else:
                    line += " "
            print(line)

    def _animate_solver(
        self,
        solution: MazeSolver,
        cfg: Config,
        maze: Maze,
        yield_every: int = 1,
    ) -> list[str]:
        """
        Animate the BFS maze solver step-by-step in the terminal.

        Args:
            - solution (MazeSolver): MazeSolver object for the current maze.
            - cfg (Config): Configuration containing entry and exit positions.
            - maze (Maze): Maze object to solve.
            - yield_every (int, optional): Yield animation every N solver step.
            Default is 1.

        Returns:
            List[str]: The final solution path from start to end.
        """

        # Store the final solution path as the animation progresses
        final_path: list[str] = []

        # Obtain a generator that yields the solver's state step-by-step
        # Each yield provides:
        #   - cur: current cell being processed
        #   - visited: set of cells already visited
        #   - frontier: set of cells in the BFS frontier
        #   - step_path: current reconstructed path from start to current
        steps_it = solution.solve_bfs_steps(
                cfg.entry,
                cfg.exit,
                yield_every=yield_every,
            )

        # Clear the terminal and hide the cursor to reduce flicker
        # \033[2J  -> clear screen
        # \033[H   -> move cursor to home
        # \033[?25l -> hide cursor
        print("\033[2J\033[H\033[?25l", end="", flush=True)

        # Iterate over the BFS solver steps
        for cur, visited, frontier, step_path in steps_it:
            # Move cursor to home to redraw maze in the same terminal position
            print("\033[H", end="", flush=True)

            # Call internal maze renderer to draw the maze at current state
            #   - 'maze' is the maze object
            #   - 'cfg' provides entry/exit positions
            #   - 'step_path' shows the path found so far
            #   - 'visited' highlights explored cells
            #   - 'frontier' highlights BFS frontier
            #   - 'current' shows the solver's current position
            self._build_maze(
                maze,
                cfg,
                step_path,
                visited=visited,
                frontier=frontier,
                current=cur,
            )

            # Update the final_path with the current reconstructed path
            final_path = step_path
            # Delay to control animation speed
            time.sleep(self.animation_speed)

        # After animation ends, restore cursor visibility
        print("\033[?25h", end="", flush=True)

        # Return the final solution path
        return final_path

    def _animate_generation(
        self,
        gen: MazeGenerator,
        cfg: Config,
        entry: tuple[int, int],
        exit: tuple[int, int],
    ) -> tuple[Maze, list[str]]:

        """
        Animate the maze generation step-by-step in the terminal.

        Args:
            gen (MazeGenerator): Maze generator object.
            cfg (Config): Configuration containing entry and exit positions.
            entry (Tuple[int,int]): Starting cell coordinates.
            exit (Tuple[int,int]): Ending cell coordinates.

        Returns:
            Tuple[Maze, List[str]]: Generated maze and its solution path.
        """

        # Clear once, then move cursor to home to reduce flicker.
        print("\033[2J\033[H\033[?25l", end="", flush=True)

        # Initialize placeholders for the final maze and the path
        final_maze: Maze | None = None
        final_path: list[str] = []

        # Iterate over each step of the maze generation
        # 'iter_generation_steps' yields tuples of:
        #   - maze: current maze state
        #   - path: the partial path reconstructed so far (can be empty)
        for maze, path in gen.iter_generation_steps(entry, exit):
            print("\033[H", end="", flush=True)
            # Draw the current maze state without the path to prevent flicker
            self._build_maze(maze, cfg, [])

            # Update the final maze and path as the generator progresses
            final_maze = maze
            final_path = path

            # Delay to control animation speed
            time.sleep(self.animation_speed)

        # Restore cursor visibility after animation ends
        print("\033[?25h", end="", flush=True)

        # Ensure generation succeeded
        if final_maze is None:
            raise RuntimeError("Generation failed")

        # Return the last maze state and its corresponding solution path
        return final_maze, final_path

    def create_maze(
        self,
        maze: Maze,
        path: list[str],
        gen: MazeGenerator,
        cfg: Config,
        solution: MazeSolver,
    ) -> None:

        """
        Main interactive menu to display, animate, and control maze behavior.

        Allows user to:
        - Show/hide solution path.
        - Change wall colors.
        - Animate maze generation and solver.
        - Change 42 stamp color.
        - Regenerate maze with a new seed.

        Args:
            maze (Maze): Initial maze object to display.
            path (List[str]): Initial solution path.
            gen (MazeGenerator): Maze generator object.
            cfg (Config): Configuration object with maze settings.
            solution (MazeSolver): Maze solver object.
        """

        current_maze = maze
        current_path = path

        while True:

            print("\033[2J\033[H", end="", flush=True)

            # Draw the current maze state and path
            self._build_maze(current_maze, cfg, current_path)

            # Calculate frames per second from animation speed
            fps = 1/self.animation_speed if self.animation_speed > 0 else 0
            perfect_type = "Perfect Maze" if cfg.perfect else "Imperfect Maze"

            # Retrieve current seed for display
            seed_display = getattr(gen, "current_seed", None)

            print(f"\n{self.wall_color}╔════════════════ Manual "
                  f"════════════════╗{self.wall_colors[0]}")
            print("   (0) Exit")
            print("   (1) Regenerate new maze")
            print("   (2) Show solution")
            print("   (3) Change maze colors")
            print(f"   (4) Animate maze generation: {self.animate_generation}")
            print(f"   (5) Animate maze solver:     {self.animate_solver}")
            print(f"   (6) Change logo color: {self.stamp_c_i}")
            print(f"  ==== Animation speed: {fps:.1f} FPS ====")
            print("   (+) Increase animation speed")
            print("   (-) Decrease animation speed")
            print(f"  ==== Seed: {seed_display}")
            print(f"  ==== Maze type: {perfect_type}")
            print(f"{self.wall_color}╚══════════════════════"
                  f"══════════════════╝{self.wall_colors[0]}")

            cmd = input("\n> ")

            # exits
            if cmd == '0':
                print("\033[2J\033[H", end="", flush=True)
                break

            # display solution
            elif cmd == '2':
                self.show_path = not self.show_path

            # change color of walls
            elif cmd == '3':
                self.color_index = (
                    (self.color_index + 1) % len(self.wall_colors)
                )
                self.wall_color = self.wall_colors[self.color_index]

            # increase speed of animation
            elif cmd == '+':
                self.animation_speed = max(0.005, self.animation_speed - 0.01)

            # decrease speed of animation
            elif cmd == '-':
                self.animation_speed = min(0.5, self.animation_speed + 0.01)

            # Toggle animation generator on/off
            elif cmd == '4':
                self.animate_generation = not self.animate_generation

            # Toggle animation solver on/off
            elif cmd == '5':
                self.animate_solver = not self.animate_solver

            # Change color of 42 Logo
            elif cmd == '6':
                self.stamp_c_i = (self.stamp_c_i + 1) % len(self.stamp_colors)
                self.stamp_color = self.stamp_colors[self.stamp_c_i]

            # Regenerate a new maze and solve it
            elif cmd == '1':
                print("\033[2J\033[H", end="", flush=True)
                print("Regenerating maze...", flush=True)

                new_seed = random.randrange(2**32)
                gen.rng = random.Random(new_seed)  # reset RNG with new seed
                gen.current_seed = new_seed        # store seed

                # Generate maze with optional animation
                if self.animate_generation:
                    current_maze, current_path = self._animate_generation(
                        gen, cfg, cfg.entry, cfg.exit,
                    )
                else:
                    current_maze = gen.generate(cfg.entry, cfg.exit)

                # Create a solver for the new maze
                solver = MazeSolver(current_maze)

                # Solve the maze with optional animation
                if self.animate_solver and self.show_path:
                    current_path = self._animate_solver(
                        solver,
                        cfg,
                        current_maze,
                        yield_every=1,
                    )
                else:
                    if not self.animate_generation:
                        current_path = solver.solve(
                            cfg.entry, cfg.exit,
                        )

                # Export maze to file
                try:
                    export_maze(
                        current_maze,
                        cfg.entry,
                        cfg.exit,
                        current_path,
                        cfg.output_file
                    )
                except ValueError as e:
                    print(f"\nError writing file: {e}", file=sys.stderr)
