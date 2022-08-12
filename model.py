import copy
import math
import pygame

pygame.font.init()

# define constants
MOVE_COST = 1
COLORS_DICT = {"#": (89, 93, 97), " ": (255, 255, 255), "A": (0, 255, 0), "B": (255, 0, 0), "-": (150, 189, 128),
               "?": (235, 231, 113)}
GREEDY_FONT = pygame.font.SysFont("comicSans", 25)
A_STAR_FONT = pygame.font.SysFont("comicSans", 15)
TEXT_COLOR = (255, 0, 0)

METRICS = ["manhattan", "euclid"]


class Tile:
    """
    A Maze is given as a set of Tiles. Each Tile can have special Attributes
    like name, distance, path cost and so on
    name: description of the tile; #: Wall, A: Start point, B: End point, " ": empty Space
    distance to end: computed distance to the B Tile -> according to a specific metric
    path cost: gets updated with time, cost of the path from start to this point
    on the way: boolean, set to true only if the tile is on the current way od the AI
    searched: boolean, set to true if agent explored the tile
    """
    def __init__(self, description, distance_to_end, path_cost=-1, on_the_way=False, searched=False):
        self.name = description
        self.distance_to_end = distance_to_end
        self.path_cost = path_cost
        self.on_the_way = on_the_way
        self.searched = searched

    def set_name(self, new_name):
        self.name = new_name

    def set_distance_to_end(self, i):
        self.distance_to_end = i

    def set_path_cost(self, i):
        self.path_cost = i

    def set_on_the_way(self, b):
        self.on_the_way = b

    def set_searched(self, b):
        self.searched = b


class Node:
    """
    paths are displayed as nodes
    path cost: cost from start A to this point
    parent: parent node -> node from which this node has been reached
    action: Action that was taken from the parent node
    state: state of the node, in this case its a position in the grid [x, y]
    """
    def __init__(self, state, parent, action, path_cost):
        self.path_cost = path_cost
        self.parent = parent
        self.action = action
        self.state = state

    def move_node_and_copy(self, action, cost):
        """
        :param action: action we want to take from the current node
        :param cost: cost to move to new state (1 in the most cases)
        :return: new node with new state
        """
        state = copy.deepcopy(self.state)
        if action == "up":
            if self.action == "down":
                return None
            state[1] -= 1
        elif action == "down":
            if self.action == "up":
                return None
            state[1] += 1
        elif action == "right":
            if self.action == "left":
                return None
            state[0] += 1
        elif action == "left":
            if self.action == "right":
                return None
            state[0] -= 1
        else:
            print("Unknown Action " + action)
            raise ValueError
        return Node(state, self, action, self.path_cost + cost)

    def printNode(self):
        """
        just for debugging purposes
        :return: print entire node information as a string
        """
        string = "State: (" + str(self.state[0]) + "," + str(self.state[1]) + "), Action: " + \
                 self.action + ", PathCost: " + str(self.path_cost)
        print(string)

    def get_nodes_on_path(self):
        """
        from a given node go to the parent until the start node is reached
        :return: list of all nodes on the way to the start node
        """
        node_list = [self]
        if self.parent:
            parent_nodes = self.parent.get_nodes_on_path()
            for node in parent_nodes:
                node_list.append(node)
        return node_list

    def get_pos_on_path(self):
        """
        from a given node go to the parent until the start node is reached
        :return: list of all position on the way to the start node
        """
        pos_list = [self.state]
        if self.parent:
            parent_pos = self.parent.get_pos_on_path()
            for states in parent_pos:
                pos_list.append(states)
        return pos_list


class StackNode:
    """
    just a simple node implementation, build for the stack data-structure
    """
    def __init__(self, el, next):
        self.el = el
        self.next = next


class Stack:
    """
    simple stack data structure with push and pop
    push: add new node to the stack
    pop: return top node of the stack and remove it
    has a length attribute since the length is not so easily accessed in a stack
    """
    length = 0
    top = None

    def __init__(self):
        pass

    def push(self, el):
        new_node = StackNode(el, self.top)
        self.top = new_node
        self.length += 1

    def pop(self):
        if self.length == 0:
            return None
        self.length -= 1
        element = self.top.el
        self.top = self.top.next
        return element


class Queue:
    """
    simple queue data structure with push and pop (works just like a list)
    push: add new node to the stack
    pop: return top node of the stack and remove it
    """
    length = 0

    def __init__(self):
        self.queue = []

    def push(self, el):
        self.queue.append(el)
        self.length += 1

    def pop(self):
        if len(self.queue) == 0:
            return None
        self.length -= 1
        return self.queue.pop(0)


class Greedy:
    """
    list data structure with push and pop function
    push: add new element
    pop: return element with the minimum distance to the end (greedy search)
    """
    length = 0

    def __init__(self, end_position, metric):
        self.elements = []
        self.end_position = end_position
        self.metric = metric

    def push(self, el):
        self.elements.append(el)
        self.length += 1

    def pop(self):
        if len(self.elements) == 0:
            return None
        self.length -= 1
        min_distance = get_distance(self.elements[0].state, self.end_position, self.metric)
        min_element = self.elements[0]
        for element in self.elements:
            temp_dist = get_distance(element.state, self.end_position, self.metric)
            if temp_dist < min_distance:
                min_element = element
                min_distance = temp_dist

        self.elements.remove(min_element)
        return copy.deepcopy(min_element)


class A_star:
    """
    list data structure with push and pop function
    push: add new element
    pop: return element with a combination of the minimum distance to the end
    and the current path cost (a* search)
    """
    length = 0

    def __init__(self, end_position, metric):
        self.elements = []
        self.end_position = end_position
        self.metric = metric

    def push(self, el):
        self.elements.append(el)
        self.length += 1

    def pop(self):
        if len(self.elements) == 0:
            return None
        self.length -= 1
        min_cost = get_distance(self.elements[0].state, self.end_position, self.metric) + self.elements[0].path_cost
        min_element = self.elements[0]
        for element in self.elements:
            temp_dist = get_distance(element.state, self.end_position, self.metric) + element.path_cost
            if temp_dist < min_cost:
                min_element = element
                min_cost = temp_dist

        self.elements.remove(min_element)
        return copy.deepcopy(min_element)


class Agent:
    """
    Agent class
    An agent is a AI which can explore a given maze with a specific search algorithm
    A frontier is a data structure which contains all nodes we still need to explore
    explored set contains all states we already explored to not double visit a state
    """
    frontier = None
    explored_set = []

    def __init__(self):
        pass

    def start_greedy(self, matrix, steps=None):
        """
        start greedy search -> go always to the node with the lowest distance
                to the end, using greedy data structure
        :param matrix: matrix which will be explored
        :param steps: steps we want to take -> for visual purpose we take small steps
        :return: result of the exploration @__explore_maze
        """
        self.frontier = Greedy(matrix.end_position, matrix.metric)
        node = Node(get_initial_state(matrix), None, None, 0)
        self.frontier.push(node)
        self.explored_set = []
        return self.__explore_maze(matrix, steps)

    def start_a_star(self, matrix, steps=None):
        """
        start a* search -> go always to the node with the lowest sum of (distance
                to the end and path cost), using a star data structure
        :param matrix: matrix which will be explored
        :param steps: steps we want to take -> for visual purpose we take small steps
        :return: result of the exploration @__explore_maze
        """
        self.frontier = A_star(matrix.end_position, matrix.metric)
        node = Node(get_initial_state(matrix), None, None, 0)
        self.frontier.push(node)
        self.explored_set = []
        return self.__explore_maze(matrix, steps)

    def start_breadth_search(self, matrix, steps=None):
        """
        start breadth first search -> using the Queue (last in, first out) to explore the maze
        :param matrix: matrix which will be explored
        :param steps: steps we want to take -> for visual purpose we take small steps
        :return: result of the exploration @__explore_maze
        """
        self.frontier = Queue()
        node = Node(get_initial_state(matrix), None, None, 0)
        self.frontier.push(node)
        self.explored_set = []
        return self.__explore_maze(matrix, steps)

    def start_depth_search(self, matrix, steps=None):
        """
        start breadth first search -> using the Stack (first in, first out) to explore the maze
        :param matrix: matrix which will be explored
        :param steps: steps we want to take -> for visual purpose we take small steps
        :return: result of the exploration @__explore_maze
        """
        self.frontier = Stack()
        node = Node(get_initial_state(matrix), None, None, 0)
        self.frontier.push(node)
        self.explored_set = []
        return self.__explore_maze(matrix, steps)

    def continue_exploring(self, matrix, steps):
        """
        since explore maze is private we can continue exploring by calling this function
        """
        return self.__explore_maze(matrix, steps)

    def __explore_maze(self, matrix, steps):
        """
        explore the given matrix but taking only this many steps
        :param matrix: matrix to explore
        :param steps: steps we take in this iteration
        :return: -) if the goal is not reached in this iteration we return False and
                the current Node
                -) if the goal was reached we return True and the last Node
                -) if the goal cant be reached we return False and None
        """
        while self.frontier.length > 0:
            element = self.frontier.pop()
            if element.state not in self.explored_set:
                matrix.set_search_tile(element.state)
                # test if end position has been reached
                if matrix.goal_test(element.state):
                    matrix.update_matrix(element)
                    return True, element
                self.explored_set.append(element.state)
                # get set of possible actions of a given state
                possible_actions = matrix.getPossibleActions(element.state)
                # iterate over all possible actions and add a node to the frontier
                for action in possible_actions:
                    new_el = element.move_node_and_copy(action, MOVE_COST)
                    if new_el is not None:
                        matrix.set_path_cost(new_el.state[1], new_el.state[0], new_el.path_cost)
                        self.frontier.push(new_el)
            # check steps
            if steps is not None:
                steps -= 1
                if steps == 0:
                    return False, element
        return False, None


class Matrix:
    """
    Matrix class: build for the maze, it can be changed, loaded, displayed and so on
    """
    def __init__(self, path=None, metric=METRICS[0]):
        """
        init function
        :param path: optional, we can load a maze from a .txt file
        :param metric: optional, if we use greedy or a star algorithm we need to
                measure the distance to the end

        tile maze is the maze given by tiles from the tile class
        simple maze is just the maze given with simple symbols like #, A, B;
                good for debugging
        initial mazes: save initial state of the maze to reset it if necessary
        """
        self.tile_maze = None
        self.simple_maze = None
        self.initial_simple_maze = None
        self.initial_tile_maze = None

        self.start_position = [0, 0]
        self.end_position = [0, 0]
        if metric not in METRICS:
            print("Unknown Metric!")
            SystemExit(0)
        self.metric = metric
        if path is not None:
            self.load_maze(path)

    def load_maze(self, path):
        """
        load a maze from a given txt file
        :param path: path to the .txt file
        """
        # open and read file
        file = open(path, 'r')
        rows = []
        x_length = 0
        y_length = 0
        for line in file:
            x_length = len(line)
            rows.append(line)
            for i in range(len(line)):
                letter = line[i]
                if letter == 'B':
                    self.end_position = [i, y_length]
                elif letter == 'A':
                    self.start_position = [i, y_length]
            y_length += 1
        # go over data and initialize tile maze and simple maze
        self.tile_maze = [[Tile('0', 0) for i in range(x_length)] for j in range(y_length)]
        self.simple_maze = [["#" for i in range(x_length)] for j in range(y_length)]
        for i in range(x_length):
            for j in range(y_length):
                self.tile_maze[j][i] = Tile(rows[j][i], get_distance([i, j], self.end_position, self.metric))
                self.simple_maze[j][i] = rows[j][i]
        self.initial_simple_maze = copy.deepcopy(self.simple_maze)
        self.initial_tile_maze = copy.deepcopy(self.tile_maze)
        file.close()

    def init_matrix(self, rows, cols, start, end):
        """
        init a matrix with empty rows, cols, start and end position
        :param rows: height of the maze
        :param cols: width of the maze
        :param start: start position
        :param end: end position
        """
        start_x = start[0]
        start_y = start[1]
        end_x = end[0]
        end_y = end[1]

        self.start_position = start
        self.end_position = end

        # initialize simple maze and tile maze as empty
        self.simple_maze = [["#" for i in range(cols)] for j in range(rows)]
        self.tile_maze = [[Tile("#", 0) for i in range(cols)] for j in range(rows)]
        for row in range(rows):
            for col in range(cols):
                if row == start_y and col == start_x:
                    self.tile_maze[row][col] = Tile("A", get_distance([col, row], self.end_position, self.metric))
                    self.simple_maze[row][col] = "A"
                elif row == end_y and col == end_x:
                    self.tile_maze[row][col] = Tile("B", get_distance([col, row], self.end_position, self.metric))
                    self.simple_maze[row][col] = "B"
                elif row != 0 and col != 0 and row != rows - 1 and col != cols - 1:
                    self.tile_maze[row][col] = Tile(" ", get_distance([col, row], self.end_position, self.metric))
                    self.simple_maze[row][col] = " "
        self.initial_simple_maze = copy.deepcopy(self.simple_maze)
        self.initial_tile_maze = copy.deepcopy(self.tile_maze)

    def getPossibleActions(self, pos):
        """
        get all possible actions from a given position
        :param pos: position the agent is in
        :return: all possible actions we can take without running into a wall
        """
        possible_actions = []
        # move Up
        pos[1] -= 1
        if self.get_simple_position(pos) != '#':
            possible_actions.append("up")
        pos[1] += 2
        # mvoe down
        if self.get_simple_position(pos) != '#':
            possible_actions.append("down")
        pos[1] -= 1
        pos[0] -= 1
        # move left
        if self.get_simple_position(pos) != '#':
            possible_actions.append("left")
        pos[0] += 2
        # move right
        if self.get_simple_position(pos) != '#':
            possible_actions.append("right")
        pos[0] -= 1
        return possible_actions

    def change_position(self, pos, new_value):
        """
        change a position in the maze (simple and tile maze) to a new value
        change initial mazes as well
        :param pos: position we want to change
        :param new_value: new value for the position
        """
        x_pos = pos[0]
        y_pos = pos[1]
        self.simple_maze[y_pos][x_pos] = new_value
        self.tile_maze[y_pos][x_pos].name = new_value
        self.initial_simple_maze[y_pos][x_pos] = new_value
        self.initial_tile_maze[y_pos][x_pos].name = new_value

    def get_simple_position(self, pos):
        """
        get description of the current position, either wall or empty ("#" or " ")
        :param pos: position we ask for
        :return: "#" or " "
        """
        x_pos = pos[0]
        y_pos = pos[1]
        if 0 <= x_pos < len(self.simple_maze[0]) and 0 <= y_pos < len(self.simple_maze):
            return self.simple_maze[y_pos][x_pos]
        else:
            print("Unavailable Position")
            raise ValueError

    def goal_test(self, pos):
        """
        test if position is the actual goal
        :param pos: position the agent is in
        :return: boolean, true if it is the goal otherwise false
        """
        if self.get_simple_position(pos) == 'B':
            return True
        else:
            return False

    def update_matrix(self, node):
        """
        updates the tile maze according to a path the agent took
        -> set searched on these tiles to true
        :param node: node the agent if in
        """
        goal_path = node.get_pos_on_path()
        for pos in goal_path:
            self.set_on_the_way_tile(pos)

    def set_search_tile(self, pos):
        """
        set a given position in the maze to searched
        it cant be the end or the start position though
        :param pos: position
        """
        if (pos[0] != self.start_position[0] or pos[1] != self.start_position[1]) and \
                (pos[0] != self.end_position[0] or pos[1] != self.end_position[1]):
            self.tile_maze[pos[1]][pos[0]].searched = True

    def set_on_the_way_tile(self, pos):
        """
        set a given position in the maze to on the way
        it cant be the end or the start position though
        :param pos: position
        """
        if (pos[0] != self.start_position[0] or pos[1] != self.start_position[1]) and \
                (pos[0] != self.end_position[0] or pos[1] != self.end_position[1]):
            self.tile_maze[pos[1]][pos[0]].on_the_way = True

    def set_path_cost(self, row, col, new_cost):
        """
        updates the cost of the path to a position in the maze
        :param row: row the agent is in
        :param col: col the agent is in
        :param new_cost: new cost of path to the tile
                (will be initialized with -1 or so)
        """
        if 0 <= row < len(self.tile_maze) and 0 <= col < len(self.tile_maze[0]):
            self.tile_maze[row][col].set_path_cost(new_cost)
        else:
            print("Unavailable Position")
            raise ValueError

    def display_tile_maze(self, pos=None):
        """
        display tile maze with the position, show searched tiles
                and on the way tiles as well
        :param pos: position we want to show
        """
        for row in range(len(self.tile_maze)):
            r = ""
            for col in range(len(self.tile_maze[0])):
                if pos is not None and row == pos[1] and col == pos[0]:
                    r += "*"
                else:
                    tile = self.tile_maze[row][col]
                    if tile.on_the_way:
                        r += "-"
                    elif tile.searched:
                        r += "?"
                    else:
                        r += self.tile_maze[row][col].name
            print(r)

    def display_simple_maze(self, pos=None):
        """
        display the simple maze with a position (if given)
        :param pos: position we want to show
        """
        for row in range(len(self.simple_maze)):
            r = ""
            for col in range(len(self.simple_maze[0])):
                if pos is not None and row == pos[1] and col == pos[0]:
                    r += "*"
                else:
                    description = self.simple_maze[row][col]
                    r += description
            print(r)

    def display_maze_pygame(self, window, square_length, offset, left_offset,
                            upper_offset, alg=None):
        """
        display the entire maze in pygame
        :param window: pygame window in use
        :param square_length: length of the square for the maze
        :param offset: distance between tiles
        :param left_offset: distance to left side of the screen
        :param upper_offset: distance to upper side of the screen
        :param alg: algorithm in use, in case we use greedy or
                a* we display more information
        """
        mult = offset + square_length
        # for every tile display information
        for row in range(len(self.tile_maze)):
            for col in range(len(self.tile_maze[0])):
                self._display_square_pygame(row, col, mult, window, square_length, alg, left_offset, upper_offset)

    def _display_square_pygame(self, row, col, mult, window, square_length,
                               algorithm, left_offset, upper_offset):
        """
        display a single square
        :param row: current row of the tile
        :param col: current col of the tile
        :param mult: offset between tiles (square length + square distance)
        :param window: window we want to display it on
        :param square_length: length of the square in the pygame maze
        :param algorithm: current algorithm, only important if greed or a*
        :param left_offset: distance to left side of the screen
        :param upper_offset: distance to upper side of the screen
        """
        tile = self.tile_maze[row][col]

        tile_name = tile.name
        # update name of the tile according to the agent progress
        if tile.on_the_way:
            tile_name = "-"
        elif tile.searched:
            tile.name = "?"
        color = COLORS_DICT.get(tile_name)
        pygame.draw.rect(window, color,
                         (col * mult + left_offset, row * mult + upper_offset, square_length, square_length))
        # in case of a greedy or a* algorithm display the cost of the tiles as well
        if tile_name != "A" and tile_name != "B" and tile_name != "#":
            if algorithm == "greed":
                if tile.path_cost != -1:
                    draw_text_greedy(window, row, col, mult, str(tile.distance_to_end), square_length,
                                     left_offset, upper_offset)
            elif algorithm == "astar":
                if tile.path_cost != -1:
                    draw_text_a_star(window, row, col, mult, str(tile.distance_to_end) + "+" + str(tile.path_cost),
                                     square_length, left_offset, upper_offset)

    def reset_matrix(self):
        """
        reset the maze to its initial state (both: simple and tile maze)
        """
        self.simple_maze = copy.deepcopy(self.initial_simple_maze)
        self.tile_maze = copy.deepcopy(self.initial_tile_maze)


def draw_text_greedy(window, row, col, mult, text, square_length,
                     left_offset, upper_offset):
    """
    init font and draw text to a square, in case of a greedy algorithm
    :param window: pygame window to draw it on
    :param row: row of the field
    :param col: column of the field
    :param mult: offset between tiles (square length + square distance)
    :param text: text to be displayed (distance to the end)
    :param square_length: length of the square in the pygame maze
    :param left_offset: distance to left side of the screen
    :param upper_offset: distance to upper side of the screen
    """
    text_drawing = GREEDY_FONT.render(text, True, TEXT_COLOR)
    window.blit(text_drawing, (left_offset + col * mult + square_length / 2 - text_drawing.get_width() / 2,
                               upper_offset + row * mult + square_length / 2 - text_drawing.get_height() / 2))


def draw_text_a_star(window, row, col, mult, text, square_length,
                     left_offset, upper_offset):
    """
    init font and draw text to a square, in case of a a* algorithm
    :param window: pygame window to draw it on
    :param row: row of the field
    :param col: column of the field
    :param mult: offset between tiles (square length + square distance)
    :param text: text to be displayed (distance to the end + current path cost)
    :param square_length: length of the square in the pygame maze
    :param left_offset: distance to left side of the screen
    :param upper_offset: distance to upper side of the screen
    """
    text_drawing = A_STAR_FONT.render(text, True, TEXT_COLOR)
    window.blit(text_drawing, (left_offset + col * mult + square_length / 2 - text_drawing.get_width() / 2,
                               upper_offset + row * mult + square_length / 2 - text_drawing.get_height() / 2))


def get_distance(pos_1, pos_2, metric):
    """
    get distance of 2 points given a metric
    :param pos_1: position 1
    :param pos_2: position 2
    :param metric: given metric in METRICS
    :return: return distance between the two positions
    """
    if metric is None:
        return 0
    x_pos = pos_1[0]
    y_pos = pos_1[1]
    end_x = pos_2[0]
    end_y = pos_2[1]
    if metric is None:
        return 1
    elif metric == "manhattan":
        return abs(x_pos - end_x) + abs(y_pos - end_y)
    elif metric == "euclid":
        return math.sqrt((x_pos - end_x) ** 2 + abs(y_pos - end_y) ** 2)
    else:
        print("Unknown Metric: " + metric)
        raise ValueError


def get_initial_state(matrix):
    """
    find the initial state of a maze
    :param matrix: maze
    :return: start position
    """
    start_pos = matrix.start_position
    return [start_pos[0], start_pos[1]]


"""METRICS = [None, "manhattan", "euclid"]
metric = METRICS[1]

maze = Matrix('maze1.txt', metric)
maze.display_tile_maze()
ai = Agent(maze, metric)

res, node = ai.start_greedy(maze, 1)
while not res:
    res, node = ai.continue_exploring(maze, 1)
    maze.display_tile_maze()
# Graphical.Pygame_Window(ai, COLORS_DICT)"""
