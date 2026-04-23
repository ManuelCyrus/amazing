from maze_generator import generate_maze
from solve.solver import solve_maze
from maze_renderer import Maze_Renderer


maze = generate_maze(cfg.width, cfg.height, cfg.seed)

start = cfg.entry
end = cfg.exit

path = solve_maze(maze, start, end, cfg.width, cfg.height)

renderer = Maze_Renderer()

renderer.create_maze(
    maze=maze,
    path=path,
    gen=None,   # se ainda não tens animação generator
    cfg=cfg
)
