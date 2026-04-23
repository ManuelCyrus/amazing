import signal
import sys
import time


try:
    from solve.solver import solve_maze_anim
except ImportError:
    def solve_maze_anim(*args): return []

class Maze_Renderer:

    def __init__(self) -> None:

        signal.signal(signal.SIGTSTP, self._handle_suspend)
        signal.signal(signal.SIGQUIT, self._handle_suspend)
        signal.signal(signal.SIGTERM, self._handle_suspend)

        self.show_path: bool = True
        self.wall_colors: list[str] = ["\033[0m", "\033[33m", "\033[34m", "\033[35m"]
        self.color_index: int = 0
        self.wall_color: str = self.wall_colors[0]
        self.animation_speed: float = 0.03

    def _handle_suspend(self, signum: int, frame: object | None) -> None:
        print("\033[?25h")  # Mostra o cursor antes de sair
        sys.exit(0)

    def _get_final_path(self, maze, start, end):
        """Resolve o labirinto internamente para garantir que o path seja exibido FILHAO COM L."""
        width, height = len(maze[0]), len(maze)
        visited = [[False] * width for _ in range(height)]
        path = []
        # (dx, dy, wall_bit, direction_char)
        directions = [(0, -1, 1, 'N'), (0, 1, 4, 'S'), (1, 0, 2, 'E'), (-1, 0, 8, 'W')]
        
        def dfs(x, y):
            if (x, y) == end: return True
            visited[y][x] = True
            for dx, dy, wall, d_char in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    if maze[y][x] & wall == 0 and not visited[ny][nx]:
                        path.append(d_char)
                        if dfs(nx, ny): return True
                        path.pop()
            return False
        
        dfs(*start)
        return path

    def save_output(self, maze, cfg, path, filename="output.txt"):
        """ExportaR o labirinto em Hexadecimal, Coordenadas e Path String."""
        try:
            with open(filename, "w") as f:
                # Matriz em Hexadecimal
                for row in maze:
                    f.write("".join(f"{cell:X}" for cell in row) + "\n")
                f.write("\n")
                # Coordenadas
                f.write(f"{cfg.entry[0]},{cfg.entry[1]}\n")
                f.write(f"{cfg.exit[0]},{cfg.exit[1]}\n")
                # Path String
                f.write("".join(path) + "\n")
            print(f"\n[✓] Exportado para: {filename}")
        except Exception as e:
            print(f"\n[!] Erro ao salvar: {e}")

    def _build_maze(self, maze, cfg, path, visited=None, frontier=None, current=None):
        """Renderiza o labirinto no terminal com cores e caracteres ASCII."""
        W_COL = self.wall_color
        ENTRY_COL, EXIT_COL = "\033[32m", "\033[31m"
        PATH_COL, VISITED_COL = "\033[96m", "\033[90m"
        FRONT_COL, CURR_COL = "\033[94m", "\033[93m"
        RESET = "\033[0m"
        BLOCK = "█"

        rows, cols = len(maze), len(maze[0])
        gh, gw = rows * 2 + 1, cols * 2 + 1
        grid = [[" " for _ in range(gw)] for _ in range(gh)]

        path_coords = set()
        path_connectors = set()
        
        if self.show_path and path:
            cx, cy = cfg.entry
            path_coords.add((cx, cy))
            for d in path:
                gx, gy = 2 * cx + 1, 2 * cy + 1
                if d == 'N': path_connectors.add((gy-1, gx, "V")); cy -= 1
                elif d == 'S': path_connectors.add((gy+1, gx, "V")); cy += 1
                elif d == 'E': path_connectors.add((gy, gx+1, "H")); cx += 1
                elif d == 'W': path_connectors.add((gy, gx-1, "H")); cx -= 1
                path_coords.add((cx, cy))

        for y, row in enumerate(maze):
            for x, val in enumerate(row):
                if (x, y) == cfg.entry: char = f"{ENTRY_COL}{BLOCK}{RESET}"
                elif (x, y) == cfg.exit: char = f"{EXIT_COL}{BLOCK}{RESET}"
                elif current and (x, y) == current: char = f"{CURR_COL}{BLOCK}{RESET}"
                elif frontier and (x, y) in frontier: char = f"{FRONT_COL}{BLOCK}{RESET}"
                elif visited and (x, y) in visited: char = f"{VISITED_COL}{BLOCK}{RESET}"
                elif (x, y) in path_coords: char = f"{PATH_COL}{BLOCK}{RESET}"
                else: char = " "
                
                grid[2*y+1][2*x+1] = char
                if val & 1: grid[2*y][2*x+1] = "─"
                if val & 2: grid[2*y+1][2*x+2] = "│"
                if val & 4: grid[2*y+2][2*x+1] = "─"
                if val & 8: grid[2*y+1][2*x] = "│"

        for gy, gx, orient in path_connectors:
            if 0 <= gy < gh and 0 <= gx < gw: grid[gy][gx] = orient

        def _get_junc(u, d, l, r):
            m = {(True,True,False,False): "│", (False,False,True,True): "─",
                 (False,True,False,True): "┌", (False,True,True,False): "┐",
                 (True,False,False,True): "└", (True,False,True,False): "┘",
                 (True,True,False,True): "├", (True,True,True,False): "┤",
                 (False,True,True,True): "┬", (True,False,True,True): "┴",
                 (True,True,True,True): "┼"}
            return m.get((u,d,l,r), " ")

        for gy in range(0, gh, 2):
            for gx in range(0, gw, 2):
                u = gy > 0 and grid[gy-1][gx] in "│V"
                d = gy < gh-1 and grid[gy+1][gx] in "│V"
                l = gx > 0 and grid[gy][gx-1] in "─H"
                r = gx < gw-1 and grid[gy][gx+1] in "─H"
                grid[gy][gx] = _get_junc(u, d, l, r)

        for gy, grid_row in enumerate(grid):
            line = ""
            for gx, ch in enumerate(grid_row):
                if ch in "─│┌┐└┘├┤┬┴┼": line += f"{W_COL}{ch}{RESET}"
                elif ch in ("H","V"): line += f"{PATH_COL}{BLOCK}{RESET}"
                else: line += ch
                if gx < gw-1:
                    nx = grid_row[gx+1]
                    if ch in "─┌└├┬┼" or nx in "─┐┘┤┬┼": line += f"{W_COL}─{RESET}"
                    elif ch == "H" or (ch == BLOCK and nx == "H"): line += f"{PATH_COL}{BLOCK}{RESET}"
                    else: line += " "
            print(line)

    def auto_solve_run(self, maze, cfg, solver_gen):
        """Executa a animação do solver e finaliza pintando o caminho real."""
        print("\033[?25l") # Esconde o cursor
        
        for state in solver_gen:
            curr = state.get("current")
            visited = state.get("visited")
            frontier = state.get("frontier")
            temp_path = state.get("path", [])
            
            print("\033[H", end="", flush=True)
            self._build_maze(maze, cfg, temp_path, visited, frontier, curr)
            time.sleep(self.animation_speed)
        
        # Pinta o caminho final sólido
        final_path = self._get_final_path(maze, cfg.entry, cfg.exit)
        self.show_path = True
        print("\033[H", end="", flush=True)
        self._build_maze(maze, cfg, final_path)
        print("\033[?25h") 
        return final_path

    def create_maze(self, maze, path, gen, cfg):
        """Menu principal do Renderizador."""
        c_maze = maze
        c_path = self._get_final_path(c_maze, cfg.entry, cfg.exit)
        
        while True:
            print("\033[2J\033[H", end="", flush=True)
            self._build_maze(c_maze, cfg, c_path)
            
            fps = 1/self.animation_speed if self.animation_speed > 0 else 0
            print(f"\n{self.wall_color}╔════════════════ PAINEL DE CONTROLE ════════════════╗{self.wall_colors[0]}")
            print(f"║ (1) Novo Labirinto    (2) Ver Rota: {'[ON] ' if self.show_path else '[OFF]'}        ║")
            print(f"║ (3) Trocar Cor        (7) AUTO-SOLVE (Animar)      ║")
            print(f"║ (+) Vel++  (-) Vel--  (8) Exportar Hex (TXT)       ║")
            print(f"║ Velocidade: {fps:.1f} FPS                              ║")
            print(f"║ (0) Sair                                           ║")
            print(f"{self.wall_color}╚════════════════════════════════════════════════════╝{self.wall_colors[0]}")
            
            try:
                cmd = input("\n> ")
            except: break

            if cmd == '0': break
            elif cmd == '1':
                c_maze = gen.generate_maze()
                c_path = self._get_final_path(c_maze, cfg.entry, cfg.exit)
            elif cmd == '2': self.show_path = not self.show_path
            elif cmd == '3':
                self.color_index = (self.color_index + 1) % len(self.wall_colors)
                self.wall_color = self.wall_colors[self.color_index]
            elif cmd == '+': self.animation_speed = max(0.005, self.animation_speed - 0.01)
            elif cmd == '-': self.animation_speed = min(0.5, self.animation_speed + 0.01)
            elif cmd == '7':
                s_gen = solve_maze_anim(c_maze, cfg.entry, cfg.exit)
                c_path = self.auto_solve_run(c_maze, cfg, s_gen)
                input("\nResolvido! [Enter] para voltar...")
            elif cmd == '8':
                self.save_output(c_maze, cfg, c_path)
                time.sleep(1)