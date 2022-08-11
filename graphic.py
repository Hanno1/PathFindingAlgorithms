import sys

import pygame

import model

pygame.font.init()
LEFT_OFFSET = 100
UPPER_OFFSET = 100
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


def init_buttons(btns, HEIGHT, WIDTH, colors_dict):
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

    btn_9 = Button(WIDTH - 80 - BUTTON_BORDER, 100 + 2 * BUTTON_BORDER, 50, 50, colors_dict.get("#"), "", "wall_state")
    btn_10 = Button(WIDTH - 80 - BUTTON_BORDER, 150 + 3 * BUTTON_BORDER, 50, 50, colors_dict.get(" "), "",
                    "empty_state")

    btn_11 = Button(800 + 3 * BUTTON_BORDER, HEIGHT - 80 - BUTTON_BORDER, 200, 80, (80, 90, 100), "Draw Mode",
                    "start_draw")
    btn_12 = Button(1000 + 4 * BUTTON_BORDER, HEIGHT - 80 - BUTTON_BORDER, 200, 80, (80, 90, 100), "Exit Draw Mode",
                    "end_draw")

    btns.append(btn_9)
    btns.append(btn_10)
    btns.append(btn_11)
    btns.append(btn_12)
    return btns


class Pygame_Window:
    def __init__(self, colors_dict):
        pygame.font.init()

        agent = model.Agent()

        matrix_height = 20
        matrix_width = 40
        offset_between_tiles = 2

        start_pos = [1, 1]
        end_pos = [38, 18]

        maze = model.Matrix(None, "manhattan")
        maze.init_matrix(matrix_height, matrix_width, start_pos, end_pos)

        HEIGHT = 900
        SQUARE_LENGTH = int(((HEIGHT - 2 * UPPER_OFFSET) / matrix_height) - offset_between_tiles)
        WIDTH = int(2 * LEFT_OFFSET + (SQUARE_LENGTH + offset_between_tiles) * matrix_width)

        WIN = pygame.display.set_mode((WIDTH, HEIGHT))

        fps = 20
        done = False
        clock = pygame.time.Clock()

        drawing = False
        draw_mode = None
        started = False
        pause_screen = False
        mouse_button_down = False

        algorithm = None

        btns = init_buttons([], HEIGHT, WIDTH, colors_dict)

        def draw_matrix(matrix):
            WIN.fill((0, 0, 0))
            matrix.display_maze_pygame(WIN, SQUARE_LENGTH, offset_between_tiles, LEFT_OFFSET, UPPER_OFFSET)
            for btn in btns:
                btn.draw(WIN)
            pygame.display.update()

        def redraw_window(done, alg):
            WIN.fill((0, 0, 0))
            result_bool = False
            if not done:
                if alg == "breadth":
                    result_bool, result_node = agent.continue_exploring(maze, agent.frontier.length)
                else:
                    result_bool, result_node = agent.continue_exploring(maze, 1)
            maze.display_maze_pygame(WIN, SQUARE_LENGTH, offset_between_tiles, LEFT_OFFSET, UPPER_OFFSET, alg)
            for btn in btns:
                btn.draw(WIN)

            pygame.display.update()
            return result_bool

        def start_algorithm(alg):
            if alg == "depth":
                agent.start_depth_search(maze, 1)
            elif alg == "breadth":
                agent.start_breadth_search(maze, 1)
            elif alg == "greed":
                agent.start_greedy(maze, 1)
            elif alg == "astar":
                agent.start_a_star(maze, 1)
            else:
                print("Unknown Algorithm " + alg)
                raise ValueError

        while True:
            clock.tick(fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    mouse_button_down = False
                if mouse_button_down or event.type == pygame.MOUSEBUTTONDOWN:
                    x_pos, y_pos = pygame.mouse.get_pos()
                    mouse_button_down = True
                    for btn in btns:
                        if btn.clicked(x_pos, y_pos):
                            if not drawing:
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
                                    pause_screen = True
                                    done = False
                                    started = False
                                    maze.reset_matrix()
                                if btn.action == "start_draw":
                                    pause_screen = True
                                    done = False
                                    drawing = True
                                    started = False
                                    maze.reset_matrix()
                            else:
                                if btn.action == "wall_state":
                                    draw_mode = "#"
                                elif btn.action == "empty_state":
                                    draw_mode = " "
                                elif btn.action == "end_draw":
                                    draw_mode = None
                                    drawing = False
                    if drawing and draw_mode is not None:
                        col = (x_pos - LEFT_OFFSET) // (SQUARE_LENGTH + offset_between_tiles)
                        row = (y_pos - UPPER_OFFSET) // (SQUARE_LENGTH + offset_between_tiles)

                        if 1 <= row < matrix_height - 1 and 1 <= col < matrix_width - 1:
                            if (row != start_pos[1] or col != start_pos[0]) and \
                                    (row != end_pos[1] or col != end_pos[0]):
                                maze.change_position([col, row], draw_mode)

            if started and not done and not pause_screen:
                done = redraw_window(done, algorithm)
            elif not started:
                draw_matrix(maze)


Pygame_Window(model.COLORS_DICT)
