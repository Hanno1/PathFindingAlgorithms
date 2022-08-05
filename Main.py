import copy
import math
import Graphical


MOVE_COST = 1


class Tile:
    def __init__(self, description, distance, on_the_way=False, searched=False):
        self.name = description
        self.distance = distance
        self.on_the_way = on_the_way
        self.searched = searched


class Node:
    def __init__(self, state, parent, action, path_cost):
        self.path_cost = path_cost
        self.action = action
        self.parent = parent
        self.state = state

    def move_node_and_copy(self, action, cost):
        state = copy.deepcopy(self.state)
        if action == "up":
            state[1] -= 1
        elif action == "down":
            state[1] += 1
        elif action == "right":
            state[0] += 1
        elif action == "left":
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
    def __init__(self, matrix, metric=None):
        self.matrix = matrix
        start = matrix.start_position
        self.initial_state = [start[0], start[1]]
        self.metric = metric

    def start_greedy(self):
        return self.explore_maze(Greedy(self.matrix.end_position, self.metric))

    def start_a_star(self):
        return self.explore_maze(A_star(self.matrix.end_position, self.metric))

    def start_breadth_search(self):
        return self.explore_maze(Queue())

    def start_depth_search(self):
        return self.explore_maze(Stack())

    def explore_maze(self, frontier):
        node = Node(self.initial_state, None, None, 0)
        frontier.push(node)
        explored_set = []

        while frontier.length > 0:
            element = frontier.pop()
            if element.state not in explored_set:
                if self.matrix.goal_test(element.state):
                    for searchedPos in explored_set:
                        self.matrix.set_search_tile(searchedPos)
                    goal_path = element.get_pos_on_path()
                    for pos in goal_path:
                        self.matrix.set_on_the_way_tile(pos)
                    return True, element
                explored_set.append(element.state)
                possible_actions = self.matrix.getPossibleActions(element.state)
                for action in possible_actions:
                    frontier.push(element.move_node_and_copy(action, MOVE_COST))
        return False, None


class Matrix:
    def __init__(self, path, metric=None):
        self.matrix = None
        self.metric = metric
        self.start_position = [0, 0]
        self.end_position = [0, 0]
        self.load_maze(path)

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
                mat[j][i] = Tile(rows[j][i], get_distance([j, i], self.end_position, self.metric))

        file.close()
        self.matrix = mat

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

    def set_search_tile(self, pos):
        if (pos[0] != self.start_position[0] or pos[1] != self.start_position[1]) and \
                (pos[0] != self.end_position[0] or pos[1] != self.end_position[1]):
            self.matrix[pos[1]][pos[0]].searched = True

    def set_on_the_way_tile(self, pos):
        if (pos[0] != self.start_position[0] or pos[1] != self.start_position[1]) and \
                (pos[0] != self.end_position[0] or pos[1] != self.end_position[1]):
            self.matrix[pos[1]][pos[0]].on_the_way = True

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


"""METRICS = [None, "manhattan", "euclid"]
metric = METRICS[1]

maze = Matrix('maze1.txt', metric)
ai = Agent(maze, metric)
done, result = ai.startGreedy()
if done:
    print(result.getPosOnPath())
    maze.displayMaze()"""
pygame_application = Graphical.Pygame_Window()
pygame_application.draw()
