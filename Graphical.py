import sys

import pygame


class Pygame_Window:
    def __init__(self, agent, algorithm):
        pygame.font.init()

        height = len(agent.matrix.matrix)
        width = len(agent.matrix.matrix[0])
        square_length = 100
        offset_between_tiles = 2

        WIDTH = (square_length + offset_between_tiles) * width
        HEIGHT = (square_length + offset_between_tiles) * height

        WIN = pygame.display.set_mode((WIDTH, HEIGHT))

        fps = 2
        done = False
        clock = pygame.time.Clock()

        if algorithm == "depth":
            agent.start_depth_search(1)
        elif algorithm == "breadth":
            agent.start_breadth_search(1)
        elif algorithm == "greed":
            agent.start_greedy(1)
        elif algorithm == "astar":
            agent.start_a_star(1)
        else:
            print("Unknown Algorithm " + algorithm)
            raise ValueError

        def redraw_window(done):
            WIN.fill((0, 0, 0))
            result_bool = False
            if not done:
                result_bool, result_node = agent.explore_maze(1)
            agent.matrix.display_maze_pygame(WIN, square_length, offset_between_tiles)
            pygame.display.update()
            return result_bool

        while True:
            clock.tick(fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            if not done:
                done = redraw_window(done)
