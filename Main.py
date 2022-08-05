import copy


class Tile:
    def __init__(self, description, heuristic=None, onTheWay=False, searched=False):
        self.name = description
        self.heuristic = heuristic
        self.onTheWay = onTheWay
        self.searched = searched


class Node:
    def __init__(self, state, parent, action, pathCost):
        self.pathCost = pathCost
        self.action = action
        self.parent = parent
        self.state = state

    def moveNodeCopy(self, action, cost):
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
        return Node(state, self, action, self.pathCost + cost)

    def printNode(self):
        string = "State: (" + str(self.state[0]) + "," + str(self.state[1]) + "), Action: " + \
                 self.action + ", PathCost: " + str(self.pathCost)
        print(string)

    def getNodesOnPath(self):
        nodeList = [self]
        if self.parent:
            parentNodes = self.parent.getNodesOnPath()
            for node in parentNodes:
                nodeList.append(node)
        return nodeList

    def getPosOnPath(self):
        posList = [self.state]
        if self.parent:
            parentPos = self.parent.getPosOnPath()
            for states in parentPos:
                posList.append(states)
        return posList


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
        newNode = StackNode(el, self.top)
        self.top = newNode
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


def getResultState(pos, action):
    x_pos = pos[0]
    y_pos = pos[1]
    if action == "up":
        return [x_pos, y_pos-1]
    elif action == "down":
        return [x_pos, y_pos+1]
    elif action == "right":
        return [x_pos+1, y_pos]
    elif action == "left":
        return [x_pos-1, y_pos]
    else:
        print("Unknown Action: " + action)
        raise ValueError


class Agent:
    def __init__(self, matrix):
        self.matrix = matrix
        start = matrix.startPosition
        self.initialState = [start[0], start[1]]

    def startBreadthSearch(self):
        return self.exploreMaze(Queue())

    def startDepthSearch(self):
        return self.exploreMaze(Stack())

    def exploreMaze(self, frontier):
        node = Node(self.initialState, None, None, 0)
        frontier.push(node)
        exploredSet = []

        while frontier.length > 0:
            element = frontier.pop()
            if element.state not in exploredSet:
                if self.matrix.goalTest(element.state):
                    for searchedPos in exploredSet:
                        self.matrix.setSearchTile(searchedPos)
                    goalPath = element.getPosOnPath()
                    for pos in goalPath:
                        self.matrix.setOnTheWayTile(pos)
                    return True, element
                exploredSet.append(element.state)
                possibleActions = self.matrix.getPossibleActions(element.state)
                for action in possibleActions:
                    frontier.push(element.moveNodeCopy(action, 1))
        return False, None


class Matrix:
    def __init__(self, path):
        self.matrix = None
        self.startPosition = [0, 0]
        self.endPosition = [0, 0]
        self.loadMaze(path)

    def loadMaze(self, path):
        file = open(path, 'r')
        rows = []
        x_length = 0
        y_length = 0
        for line in file:
            x_length = len(line)
            y_length += 1
            rows.append(line)
        mat = [[Tile('0') for i in range(x_length)] for j in range(y_length)]
        for i in range(x_length):
            for j in range(y_length):
                mat[j][i] = Tile(rows[j][i])
                if rows[j][i] == 'A':
                    self.startPosition = [i, j]
                elif rows[j][i] == 'B':
                    self.endPosition = [i, j]
        file.close()
        self.matrix = mat

    def getPossibleActions(self, pos):
        possibleActions = []
        # move Up
        pos[1] -= 1
        if self.getPositionValue(pos) != '#':
            possibleActions.append("up")
        pos[1] += 2
        if self.getPositionValue(pos) != '#':
            possibleActions.append("down")
        pos[1] -= 1
        pos[0] -= 1
        if self.getPositionValue(pos) != '#':
            possibleActions.append("left")
        pos[0] += 2
        if self.getPositionValue(pos) != '#':
            possibleActions.append("right")
        pos[0] -= 1
        return possibleActions

    def getPositionValue(self, pos):
        x_pos = pos[0]
        y_pos = pos[1]
        if 0 <= x_pos < len(self.matrix[0]) and 0 <= y_pos < len(self.matrix):
            return self.matrix[y_pos][x_pos].name
        else:
            print("Unavailable Position")
            raise ValueError

    def goalTest(self, pos):
        if self.getPositionValue(pos) == 'B':
            return True
        else:
            return False

    def setSearchTile(self, pos):
        if (pos[0] != self.startPosition[0] or pos[1] != self.startPosition[1]) and \
                (pos[0] != self.endPosition[0] or pos[1] != self.endPosition[1]):
            self.matrix[pos[1]][pos[0]].searched = True

    def setOnTheWayTile(self, pos):
        if (pos[0] != self.startPosition[0] or pos[1] != self.startPosition[1]) and \
                (pos[0] != self.endPosition[0] or pos[1] != self.endPosition[1]):
            self.matrix[pos[1]][pos[0]].onTheWay = True

    def displayMaze(self, pos=None):
        for row in range(len(self.matrix)):
            r = ""
            for col in range(len(self.matrix[0])):
                if pos is not None and row == pos[1] and col == pos[0]:
                    r += "*"
                else:
                    tile = self.matrix[row][col]
                    if tile.onTheWay:
                        r += "-"
                    elif tile.searched:
                        r += "?"
                    else:
                        r += self.matrix[row][col].name
            print(r)


maze = Matrix('maze1.txt')
ai = Agent(maze)
done, result = ai.startBreadthSearch()
print(done)
if done:
    print(result.getPosOnPath())
    maze.displayMaze()
