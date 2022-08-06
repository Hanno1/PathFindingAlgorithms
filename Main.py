import copy
import math
import pygame
import Graphical


pygame.font.init()

MOVE_COST = 1
COLORS_DICT = {"#": (0, 0, 0), " ": (255, 255, 255), "A": (0, 255, 0), "B": (255, 0, 0), "-": (150, 189, 128),
               "?": (235, 231, 113)}
FONT = pygame.font.SysFont("comicSans", 50)
TEXT_COLOR = (255, 0, 0)


class Tile:
    def __init__(self, description, distance_to_end, path_cost=-1, on_the_way=False, searched=False):
        self.name = description
        self.distance_to_end = distance_to_end
        self.path_cost = path_cost
        self.on_the_way = on_the_way
        self.searched = searched

    def set_distance_to_end(self, i):
        self.distance_to_end = i

    def set_path_cost(self, i):
        self.path_cost = i

    def set_on_the_way(self, b):
        self.on_the_way = b

    def set_searched(self, b):
        self.searched = b


class Node:
    def __init__(self, state, parent, action, path_cost):
        self.path_cost = path_cost
        self.action = action
        self.parent = parent
        self.state = state

    def move_node_and_copy(self, action, cost):
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
        string = "State: (" + str(self.state[0]) + "," + str(self.state[1]) + "), Action: " + \
                 self.action + ", PathCost: " + str(self.path_cost)
        print(string)

    def get_nodes_on_path(self):
        node_list = [self]
        if self.parent:
            parent_nodes = self.parent.get_nodes_on_path()
            for node in parent_nodes:
                node_list.append(node)
        return node_list

    def get_pos_on_path(self):
        pos_list = [self.state]
        if self.parent:
            parent_pos = self.parent.get_pos_on_path()
            for states in parent_pos:
                pos_list.append(states)
        return pos_list


class StackNode:
    def __init__(self, el, next):
        self.el = el
        self.next = next


class Stack:
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


def getResultState(pos, action):
    x_pos = pos[0]
    y_pos = pos[1]
    if action == "up":
        return [x_pos, y_pos - 1]
    elif action == "down":
        return [x_pos, y_pos + 1]
    elif action == "right":
        return [x_pos + 1, y_pos]
    elif action == "left":
        return [x_pos - 1, y_pos]
    else:
        print("Unknown Action: " + action)
        raise ValueError


class Agent:
    frontier = None
    explored_set = []

    def __init__(self, matrix, metric=None):
        self.matrix = matrix
        start = matrix.start_position
        self.initial_state = [start[0], start[1]]
        self.metric = metric

    def start_greedy(self, steps=None):
        self.frontier = Greedy(self.matrix.end_position, self.metric)
        node = Node(self.initial_state, None, None, 0)
        self.frontier.push(node)
        self.explored_set = []
        return self.explore_maze(steps)

    def start_a_star(self, steps=None):
        self.frontier = A_star(self.matrix.end_position, self.metric)
        node = Node(self.initial_state, None, None, 0)
        self.frontier.push(node)
        self.explored_set = []
        return self.explore_maze(steps)

    def start_breadth_search(self, steps=None):
        self.frontier = Queue()
        node = Node(self.initial_state, None, None, 0)
        self.frontier.push(node)
        self.explored_set = []
        return self.explore_maze(steps)

    def start_depth_search(self, steps=None):
        self.frontier = Stack()
        node = Node(self.initial_state, None, None, 0)
        self.frontier.push(node)
        self.explored_set = []
        return self.explore_maze(steps)

    def explore_maze(self, steps):
        while self.frontier.length > 0:
            element = self.frontier.pop()
            if element.state not in self.explored_set:
                self.matrix.set_search_tile(element.state)
                if self.matrix.goal_test(element.state):
                    self.matrix.update_matrix(element)
                    return True, element
                self.explored_set.append(element.state)
                possible_actions = self.matrix.getPossibleActions(element.state)
                for action in possible_actions:
                    new_el = element.move_node_and_copy(action, MOVE_COST)
                    if new_el is not None:
                        self.matrix.set_path_cost(new_el.state[1], new_el.state[0], new_el.path_cost)
                        self.frontier.push(new_el)
            if steps is not None:
                steps -= 1
                if steps == 0:
                    return False, None
        return False, None

    def reset(self):
        self.frontier = Stack()
        self.explored_set = []
        self.matrix.reset()


class Matrix:
    def __init__(self, path, metric=None):
        self.matrix = None
        self.metric = metric
        self.start_position = [0, 0]
        self.end_position = [0, 0]
        self.load_maze(path)
        self.start_matrix = copy.deepcopy(self.matrix)

    def load_maze(self, path):
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

        mat = [[Tile('0', 0) for i in range(x_length)] for j in range(y_length)]
        for i in range(x_length):
            for j in range(y_length):
                mat[j][i] = Tile(rows[j][i], get_distance([i, j], self.end_position, self.metric))

        file.close()
        self.matrix = mat

    def reset(self):
        self.matrix = copy.deepcopy(self.start_matrix)

    def getPossibleActions(self, pos):
        possible_actions = []
        # move Up
        pos[1] -= 1
        if self.get_position_value(pos) != '#':
            possible_actions.append("up")
        pos[1] += 2
        if self.get_position_value(pos) != '#':
            possible_actions.append("down")
        pos[1] -= 1
        pos[0] -= 1
        if self.get_position_value(pos) != '#':
            possible_actions.append("left")
        pos[0] += 2
        if self.get_position_value(pos) != '#':
            possible_actions.append("right")
        pos[0] -= 1
        return possible_actions

    def get_position_value(self, pos):
        x_pos = pos[0]
        y_pos = pos[1]
        if 0 <= x_pos < len(self.matrix[0]) and 0 <= y_pos < len(self.matrix):
            return self.matrix[y_pos][x_pos].name
        else:
            print("Unavailable Position")
            raise ValueError

    def goal_test(self, pos):
        if self.get_position_value(pos) == 'B':
            return True
        else:
            return False

    def update_matrix(self, element):
        goal_path = element.get_pos_on_path()
        for pos in goal_path:
            self.set_on_the_way_tile(pos)

    def set_search_tile(self, pos):
        if (pos[0] != self.start_position[0] or pos[1] != self.start_position[1]) and \
                (pos[0] != self.end_position[0] or pos[1] != self.end_position[1]):
            self.matrix[pos[1]][pos[0]].searched = True

    def set_on_the_way_tile(self, pos):
        if (pos[0] != self.start_position[0] or pos[1] != self.start_position[1]) and \
                (pos[0] != self.end_position[0] or pos[1] != self.end_position[1]):
            self.matrix[pos[1]][pos[0]].on_the_way = True

    def remove_on_the_way_tile(self, pos):
        self.matrix[pos[1]][pos[0]].on_the_way = False

    def display_maze(self, pos=None):
        for row in range(len(self.matrix)):
            r = ""
            for col in range(len(self.matrix[0])):
                if pos is not None and row == pos[1] and col == pos[0]:
                    r += "*"
                else:
                    tile = self.matrix[row][col]
                    if tile.on_the_way:
                        r += "-"
                    elif tile.searched:
                        r += "?"
                    else:
                        r += self.matrix[row][col].name
            print(r)

    def display_maze_pygame(self, window, square_length, offset, alg, left_offset, upper_offset):
        mult = offset + square_length
        for row in range(len(self.matrix)):
            for col in range(len(self.matrix[0])):
                self._display_square_pygame(row, col, mult, window, square_length, alg, left_offset, upper_offset)

    def set_path_cost(self, row, col, cost):
        self.matrix[row][col].path_cost = cost

    def _display_square_pygame(self, row, col, mult, window, square_length, algorithm, left_offset, upper_offset):
        tile = self.matrix[row][col]
        tile_name = tile.name
        if tile.on_the_way:
            tile_name = "-"
        elif tile.searched:
            tile.name = "?"
        color = COLORS_DICT.get(tile_name)
        pygame.draw.rect(window, color, (col * mult + left_offset, row * mult + upper_offset, square_length, square_length))
        if tile_name != "A" and tile_name != "B" and tile_name != "#":
            if algorithm == "greed":
                if tile.path_cost != -1:
                    draw_text(window, row, col, mult, str(tile.distance_to_end), square_length,
                              left_offset, upper_offset)
            elif algorithm == "astar":
                if tile.path_cost != -1:
                    draw_text(window, row, col, mult, str(tile.distance_to_end) + "+" + str(tile.path_cost),
                              square_length, left_offset, upper_offset)


def draw_text(window, row, col, mult, text, square_length, left_offset, upper_offset):
    text_drawing = FONT.render(text, True, TEXT_COLOR)
    window.blit(text_drawing, (left_offset + col * mult + square_length / 2 - text_drawing.get_width() / 2,
                               upper_offset + row * mult + square_length / 2 - text_drawing.get_height() / 2))


def get_distance(pos_1, pos_2, metric):
    if metric is None:
        return 0
    x_pos = pos_1[0]
    y_pos = pos_1[1]
    end_x = pos_2[0]
    end_y = pos_2[1]
    if metric == "manhattan":
        return abs(x_pos - end_x) + abs(y_pos - end_y)
    elif metric == "euclid":
        return math.sqrt((x_pos - end_x) ** 2 + abs(y_pos - end_y) ** 2)
    else:
        print("Unknown Metric: " + metric)
        raise ValueError


"""maze = Matrix('maze1.txt', metric)
ai = Agent(maze, metric)
done, result = ai.start_greedy(1)
if done:
    print(result.getPosOnPath())
maze.display_maze()"""
METRICS = [None, "manhattan", "euclid"]
metric = METRICS[1]

maze = Matrix('maze1.txt', metric)
ai = Agent(maze, metric)
Graphical.Pygame_Window(ai)
