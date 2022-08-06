import sys

import pygame

pygame.font.init()
LEFT_OFFSET = 100
UPPER_OFFSET = 100
SQUARE_LENGTH = 100
SQUARE_BORDER = 2
TEXT_COLOR = (100, 100, 200)
BUTTON_BORDER = 10


ACTIONS = ["breadth", "depth", "greed", "astar"]


class Button:
    BUTTON_FONT = pygame.font.SysFont("comicSans", 40)

    def __init__(self, x, y, width, height, color, text, action):
        self.x_index = x
        self.y_index = y
        self.x = self.x_index + BUTTON_BORDER
        self.y = self.y_index + BUTTON_BORDER
        self.width = width
        self.height = height
        self.color = color
        self.text = text
        self.text_color = TEXT_COLOR
        self.action = action

    def draw(self, window):
        if self.text != "":
            button = self.BUTTON_FONT.render(self.text, True, self.text_color)
        else:
            button = self.BUTTON_FONT.render("", True, self.color)
        pygame.draw.rect(window, (0, 0, 0), (self.x, self.y, self.width, self.height))
        pygame.draw.rect(window, self.color, (self.x + SQUARE_BORDER, self.y + SQUARE_BORDER,
                                              self.width - 2 * SQUARE_BORDER, self.height - 2 * SQUARE_BORDER))
        window.blit(button, (self.x + self.width / 2 - button.get_width() / 2,
                             self.y + self.height / 2 - button.get_height() / 2))

    def clicked(self, x_pos, y_pos):
        if self.x <= x_pos <= self.x + self.width and self.y <= y_pos <= self.y + self.height:
            return True
        else:
            return False


class Pygame_Window:
    def __init__(self, agent):
        pygame.font.init()

        height = len(agent.matrix.matrix)
        width = len(agent.matrix.matrix[0])
        offset_between_tiles = 2

        WIDTH = (SQUARE_LENGTH + offset_between_tiles) * width + 2 * LEFT_OFFSET
        HEIGHT = (SQUARE_LENGTH + offset_between_tiles) * height + 2 * UPPER_OFFSET

        WIN = pygame.display.set_mode((WIDTH, HEIGHT))

        fps = 2
        done = False
        clock = pygame.time.Clock()

        pause_screen = False
        started = False

        btns = []
        btn_0 = Button(0, 0, 200, 80, (80, 90, 100), "Breadth Search", "breadth")
        btn_1 = Button(200 + BUTTON_BORDER, 0, 200, 80, (80, 90, 100), "Depth Search", "depth")
        btn_2 = Button(400 + 2 * BUTTON_BORDER, 0, 200, 80, (80, 90, 100), "Greedy Search", "greed")
        btn_3 = Button(600 + 3 * BUTTON_BORDER, 0, 200, 80, (80, 90, 100), "A* Search", "astar")

        btn_4 = Button(0, HEIGHT - 80 - BUTTON_BORDER, 200, 80, (80, 90, 100), "Pause", "pause")
        btn_5 = Button(200 + BUTTON_BORDER, HEIGHT - 80 - BUTTON_BORDER, 200, 80, (80, 90, 100), "Continue", "continue")
        btn_6 = Button(400 + 2 * BUTTON_BORDER, HEIGHT - 80 - BUTTON_BORDER, 200, 80, (80, 90, 100), "Reset", "reset")

        btns.append(btn_0)
        btns.append(btn_1)
        btns.append(btn_2)
        btns.append(btn_3)
        btns.append(btn_4)
        btns.append(btn_5)
        btns.append(btn_6)

        def draw_matrix(alg):
            WIN.fill((0, 0, 0))
            agent.matrix.display_maze_pygame(WIN, SQUARE_LENGTH, offset_between_tiles, alg, LEFT_OFFSET, UPPER_OFFSET)
            for btn in btns:
                btn.draw(WIN)
            pygame.display.update()

        def redraw_window(done, alg):
            WIN.fill((0, 0, 0))
            result_bool = False
            if not done:
                if alg == "breadth":
                    result_bool, result_node = agent.explore_maze(agent.frontier.length)
                else:
                    result_bool, result_node = agent.explore_maze(1)
            agent.matrix.display_maze_pygame(WIN, SQUARE_LENGTH, offset_between_tiles, alg, LEFT_OFFSET, UPPER_OFFSET)
            for btn in btns:
                btn.draw(WIN)

            pygame.display.update()
            return result_bool

        def start_algorithm(alg):
            if alg == "depth":
                agent.start_depth_search(1)
            elif alg == "breadth":
                agent.start_breadth_search(1)
            elif alg == "greed":
                agent.start_greedy(1)
            elif alg == "astar":
                agent.start_a_star(1)
            else:
                print("Unknown Algorithm " + alg)
                raise ValueError

        algorithm = "breadth"

        while True:
            clock.tick(fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x_pos, y_pos = pygame.mouse.get_pos()
                    for btn in btns:
                        if btn.clicked(x_pos, y_pos):
                            if not started and btn.action in ACTIONS:
                                start_algorithm(btn.action)
                                algorithm = btn.action
                                pause_screen = False
                                started = True
                            if btn.action == "pause":
                                pause_screen = True
                            if btn.action == "continue":
                                pause_screen = False
                            if btn.action == "reset":
                                agent.reset()
                                pause_screen = True
                                done = False
                                started = False
            if started and not done and not pause_screen:
                done = redraw_window(done, algorithm)
            if not started:
                draw_matrix(algorithm)
