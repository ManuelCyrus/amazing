import signal
import sys
import time
import random
from solve import MazeGenerator, Maze, MazeSolver
from config import Config
from solve.maze_generator import export_maze


class Maze_Renderer:

    def __init__(self) -> None:

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

        """Renderiza o labirinto no terminal com cores e caracteres ASCII."""
        WALL_COLOR = self.wall_color  # Set by user interaction
        ENTRY_COLOR = "\033[32m"      # Green
        EXIT_COLOR = "\033[31m"       # Red
        PATH_COLOR = "\033[96m"       # Bright cyan for solution path
        # STAMP_COLOR = "\033[93m"      # Bright yellow for the 42 stamp
        RESET = "\033[0m"             # reset color to default
        BLOCK = "█"

        # Convert path directions to coordinates and connectors
        path_coords = set()
        path_connectors: set[tuple[int, int, str]] = set()
        stamp_coords: set[tuple[int, int]] = getattr(
            maze, "stamp42", set()
        )
        has_stamp = bool(stamp_coords)

        if self.show_path and path:
            x, y = cfg.entry
            path_coords.add((x, y))  # Include entry in path
            for direction in path:
                gx, gy = 2 * x + 1, 2 * y + 1
                if direction == 'N':
                    path_connectors.add((gy - 1, gx, "V"))
                    y -= 1
                elif direction == 'S':
                    path_connectors.add((gy + 1, gx, "V"))
                    y += 1
                elif direction == 'E':
                    path_connectors.add((gy, gx + 1, "H"))
                    x += 1
                elif direction == 'W':
                    path_connectors.add((gy, gx - 1, "H"))
                    x -= 1
                else:
                    # Skip invalid directions
                    continue
                path_coords.add((x, y))
            # Ensure exit is included
            path_coords.add(cfg.exit)

        wall_chars = {
            "─",
            "│",
            "┌",
            "┐",
            "└",
            "┘",
            "├",
            "┤",
            "┬",
            "┴",
            "┼",
        }

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

        rows = len(maze.grid)
        cols = len(maze.grid[0]) if rows > 0 else 0
        grid_h = rows * 2 + 1
        grid_w = cols * 2 + 1
        grid: list[list[str]] = [
            [" " for _ in range(grid_w)] for _ in range(grid_h)
        ]

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
                    center_char = "\033[95m█\033[0m"  # cursor
                elif frontier and (x, y) in frontier:
                    center_char = "\033[94m█\033[0m"  # frontier
                elif visited and (x, y) in visited:
                    center_char = "\033[90m█\033[0m"  # visited
                elif (x, y) in path_coords:
                    center_char = f"{PATH_COLOR}{BLOCK}{RESET}"
                else:
                    center_char = " "

                grid[2 * y + 1][2 * x + 1] = center_char

                # 2) Build the walls using bitmasking
                # (cell_value is 0-15: N=1, E=2, S=4, W=8)
                n_wall_exists = bool(cell_value & 1)
                e_wall_exists = bool(cell_value & 2)
                s_wall_exists = bool(cell_value & 4)
                w_wall_exists = bool(cell_value & 8)

                if n_wall_exists:
                    grid[2 * y][2 * x + 1] = "─"
                if s_wall_exists:
                    grid[2 * y + 2][2 * x + 1] = "─"
                if w_wall_exists:
                    grid[2 * y + 1][2 * x] = "│"
                if e_wall_exists:
                    grid[2 * y + 1][2 * x + 2] = "│"

        # 3) Add path connectors so color is continuous between cells
        for gy, gx, orient in path_connectors:
            if 0 <= gy < grid_h and 0 <= gx < grid_w:
                if grid[gy][gx] == " ":
                    grid[gy][gx] = orient

        path_center_grid = {
            (2 * y + 1, 2 * x + 1) for (x, y) in path_coords
        }

        # 4) Resolve junctions for continuous lines
        for gy in range(0, grid_h, 2):
            for gx in range(0, grid_w, 2):
                up = gy > 0 and grid[gy - 1][gx] == "│"
                down = gy < grid_h - 1 and grid[gy + 1][gx] == "│"
                left = gx > 0 and grid[gy][gx - 1] == "─"
                right = gx < grid_w - 1 and grid[gy][gx + 1] == "─"
                grid[gy][gx] = _junction_char(up, down, left, right)

        # 5) Print the grid with colored walls and path
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

        """Animate solver (BFS) step-by-step.

        Maze generation is instantaneous; only the solver search is animated.
        """
        final_path: list[str] = []

        # TO CHECK URGENT
        steps_it = solution.solve_bfs_steps(
                cfg.entry,
                cfg.exit,
                yield_every=yield_every,
            )

        # Clear once, then only move cursor to home to reduce flicker.
        print("\033[2J\033[H\033[?25l", end="", flush=True)

        for cur, visited, frontier, step_path in steps_it:
            print("\033[H", end="", flush=True)
            self._build_maze(
                maze,
                cfg,
                step_path,
                visited=visited,
                frontier=frontier,
                current=cur,
            )

            final_path = step_path
            time.sleep(self.animation_speed)

        print("\033[?25h", end="", flush=True)
        return final_path

    def _animate_generation(
        self,
        gen: MazeGenerator,
        cfg: Config,
        entry: tuple[int, int],
        exit: tuple[int, int],
    ) -> tuple[Maze, list[str]]:
        """Animate maze generation step-by-step.

        Returns the final maze and its solution path.
        """
        # Clear once, then only move cursor to home to reduce flicker.
        print("\033[2J\033[H\033[?25l", end="", flush=True)

        final_maze: Maze | None = None
        final_path: list[str] = []

        # TO CHECK URGENT
        for maze, path in gen.iter_generation_steps(entry, exit):
            print("\033[H", end="", flush=True)
            # Hide path during generation to avoid flashing the solution.
            self._build_maze(maze, cfg, [])
            final_maze = maze
            final_path = path
            time.sleep(self.animation_speed)

        print("\033[?25h", end="", flush=True)

        if final_maze is None:
            raise RuntimeError("Generation failed")

        return final_maze, final_path

    def create_maze(
        self,
        maze: Maze,
        path: list[str],
        gen: MazeGenerator,
        cfg: Config,
        solution: MazeSolver,
    ) -> None:

        """Menu principal do Renderizador."""
        current_maze = maze
        current_path = path

        while True:

            print("\033[2J\033[H", end="", flush=True)

            self._build_maze(current_maze, cfg, current_path)

            fps = 1/self.animation_speed if self.animation_speed > 0 else 0
            perfect_type = "Perfect Maze" if cfg.perfect else "Imperfect Maze"
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
                ########
                # QUALITY OF LIFE, clear console when press 0 then break
                ########
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

            ######
            #   Added 42 logo color change
            ######
            # Change color of 42 Logo
            elif cmd == '6':
                self.stamp_c_i = (self.stamp_c_i + 1) % len(self.stamp_colors)
                self.stamp_color = self.stamp_colors[self.stamp_c_i]

            # Regenerate a new maze and solve it
            elif cmd == '1':
                print("\033[2J\033[H", end="", flush=True)
                print("Regenerating maze...", flush=True)
                ########
                # Generate new seed for new maze
                ########
                new_seed = random.randrange(2**32)
                gen.rng = random.Random(new_seed)  # reset RNG with new seed
                gen.current_seed = new_seed        # store it in the generator
                # Checks if need animate generation or not
                if self.animate_generation:
                    current_maze, current_path = self._animate_generation(
                        gen, cfg, cfg.entry, cfg.exit,
                    )
                else:
                    # MAZE GENERATOR
                    current_maze = gen.generate(cfg.entry, cfg.exit)

                #######
                # Making sure the solver uses the current new maze
                #######
                solver = MazeSolver(current_maze)
                # Checks if need animate solver or not
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
                # Update output file
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
