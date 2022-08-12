import sys
import pygame
import model

# constants for the window and for pygame
pygame.font.init()
LEFT_OFFSET = 100
UPPER_OFFSET = 100
SQUARE_BORDER = 2
TEXT_COLOR = (100, 100, 200)
BUTTON_BORDER = 10

# possible algorithm for searching
ACTIONS = ["breadth", "depth", "greed", "astar"]


class Button:
    """
    Button class for pygame. A button has different attributes and can be easily drawn
            by calling button.draw
    """
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
        """
        draw a button on the given pygame window
        :param window: window to draw on
        """
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
        """
        :param x_pos: x position of the mouseclick
        :param y_pos: y position of the mouseclick
        :return: boolean, true if the button was clicked
                (x, y align with boundaries), false if not
        """
        if self.x <= x_pos <= self.x + self.width and self.y <= y_pos <= self.y + self.height:
            return True
        else:
            return False


def init_buttons(HEIGHT, WIDTH, colors_dict):
    """
    init all buttons with a given height, width and colors
            add them to the btns list
    :param HEIGHT: height of the buttons
    :param WIDTH: width of the buttons
    :param colors_dict: in case we change the tiles of the maze, we need a button
            with a specific color
    :return: list of all buttons
    """
    btns = []

    # buttons for starting a algorithm
    btn_0 = Button(0, 0, 200, 80, (80, 90, 100), "Breadth Search", "breadth")
    btn_1 = Button(200 + BUTTON_BORDER, 0, 200, 80, (80, 90, 100), "Depth Search", "depth")
    btn_2 = Button(400 + 2 * BUTTON_BORDER, 0, 200, 80, (80, 90, 100), "Greedy Search", "greed")
    btn_3 = Button(600 + 3 * BUTTON_BORDER, 0, 200, 80, (80, 90, 100), "A* Search", "astar")

    # buttons for pausing, continuing or resetting the algorithm / maze
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

    # buttons for the draw mode, if we change the maze
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
    """
    main pygame class, init window, maze, agent and so on
    """
    def __init__(self, colors_dict):
        pygame.font.init()

        agent = model.Agent()

        # init maze parameters, the height is set to a constant value,
        # the width depends on the length of the maze
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

        # different booleans for different modes
        drawing = False
        draw_mode = None
        started = False
        pause_screen = False
        mouse_button_down = False

        # algorithm that will be executed
        algorithm = None

        btns = init_buttons(HEIGHT, WIDTH, colors_dict)

        def draw_matrix(matrix):
            """
            display just a normal matrix and the buttons,
                    no steps or algorithm used
            :param matrix: maze to be displayed
            """
            WIN.fill((0, 0, 0))
            matrix.display_maze_pygame(WIN, SQUARE_LENGTH, offset_between_tiles, LEFT_OFFSET, UPPER_OFFSET)
            for btn in btns:
                btn.draw(WIN)
            pygame.display.update()

        def redraw_window(done, alg):
            """
            display just a normal matrix and the buttons,
                    display current state of the algorithm as well (searched / on the way)
            :param done: if done don't continue the algorithm
            :param alg: current algorithm that has to be executed
            :return: if we reached the B node return true, else return false
            """
            WIN.fill((0, 0, 0))
            result_bool = False
            # explore maze, in case of breadth search we take other step size
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
            """
            start the algorithm
            :param alg: algorithm we want to start
            """
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
            """
            game loop, check for events and draw on the screen
            """
            clock.tick(fps)
            for event in pygame.event.get():
                # check for quit event
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # we want to draw if the mouse is moving while the mouse button is held
                # therefore we check then the mouse is pressed or released
                if event.type == pygame.MOUSEBUTTONUP:
                    mouse_button_down = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x_pos, y_pos = pygame.mouse.get_pos()
                    mouse_button_down = True
                    for btn in btns:
                        # check if buttons have been clicked
                        if btn.clicked(x_pos, y_pos):
                            if not drawing:
                                # start algorithm depending on the button pressed
                                if not started and btn.action in ACTIONS:
                                    start_algorithm(btn.action)
                                    algorithm = btn.action
                                    pause_screen = False
                                    started = True
                                    break
                                # pause the screen, don't continue exploring
                                if btn.action == "pause":
                                    pause_screen = True
                                    break
                                # if pause screen is true this will continue the exploration
                                if btn.action == "continue":
                                    pause_screen = False
                                    break
                                # reset the maze to its initial state
                                if btn.action == "reset":
                                    pause_screen = True
                                    done = False
                                    started = False
                                    maze.reset_matrix()
                                    break
                                # enter draw mode
                                if btn.action == "start_draw":
                                    pause_screen = True
                                    done = False
                                    drawing = True
                                    started = False
                                    maze.reset_matrix()
                                    break
                            else:
                                # if drawing is active, we check only 3 buttons: wall, empty and end draw mode
                                if btn.action == "wall_state":
                                    draw_mode = "#"
                                elif btn.action == "empty_state":
                                    draw_mode = " "
                                elif btn.action == "end_draw":
                                    draw_mode = None
                                    drawing = False
                if mouse_button_down:
                    # check if the mouse button is down, if this is the case and we are drawing
                    # and a option to draw is chose we check the mouse position and change the field
                    x_pos, y_pos = pygame.mouse.get_pos()
                    if drawing and draw_mode is not None:
                        col = (x_pos - LEFT_OFFSET) // (SQUARE_LENGTH + offset_between_tiles)
                        row = (y_pos - UPPER_OFFSET) // (SQUARE_LENGTH + offset_between_tiles)

                        # test for boundaries
                        if 1 <= row < matrix_height - 1 and 1 <= col < matrix_width - 1:
                            if (row != start_pos[1] or col != start_pos[0]) and \
                                    (row != end_pos[1] or col != end_pos[0]):
                                maze.change_position([col, row], draw_mode)

            if started and not done and not pause_screen:
                # update the screen and keep exploring
                done = redraw_window(done, algorithm)
            elif not started:
                # just draw the current maze, used for draw mode
                draw_matrix(maze)


Pygame_Window(model.COLORS_DICT)
