import sys
import math
from random import *
import copy

# Deliver more amadeusium to hq (left side of the map) than your opponent. Use radars to find amadeusium but beware of traps!

# height: size of the map
width, height = [int(i) for i in input().split()]

NONE = -1
ROBOT_ALLY = 0
ROBOT_ENEMY = 1
HOLE = 1
RADAR = 2
TRAP = 3
AMADEUSIUM = 4
ORE_UNKNOW = 5
PREDICT_AMADEUSIUM = 6
NEED_RADAR = 7
NEED_NO_HOLE = 8
NEED_REQUEST_RADAR = 9
NEED_BIG_RADAR = 10
INIT = 100

HOME = 20
WAITING = 21
DANGEROUS = 22

class Pos:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return '({},{})'.format(self.x, self.y)

    def distance(self, pos):
        return abs(self.x - pos.x) + abs(self.y - pos.y)

class Entity(Pos):
    def __init__(self, x, y, type, id):
        super().__init__(x, y)
        self.type = type
        self.id = id

class Robot(Entity):
    def __init__(self, x, y, type, id, item):
        super().__init__(x, y, type, id)
        self.item = item

    def __str__(self):
        return '({},{},type {},id {},item {})'.format(self.x, self.y,self.type,self.id,self.item)

    def has_ore(self):
        return self.item == AMADEUSIUM

    def is_dead(self):
        return self.x == -1 and self.y == -1

    @staticmethod
    def move(x, y, message=""):
        print(f"MOVE {x} {y} {message}")

    @staticmethod
    def wait(message=""):
        print(f"WAIT {message}")

    @staticmethod
    def dig(x, y, message=""):
        print(f"DIG {x} {y} {message}")

    @staticmethod
    def request(requested_item, message=""):
        if requested_item == RADAR:
            print(f"REQUEST RADAR {message}")
        elif requested_item == TRAP:
            print(f"REQUEST TRAP {message}")
        else:
            raise Exception(f"Unknown item {requested_item}")

class Cell(Pos):
    def __init__(self, x, y, amadeusium, hole):
        super().__init__(x, y)
        self.amadeusium = amadeusium
        self.hole = hole

    def __str__(self):
        return 'x {} y {} amadeusium {} hole {}'.format(
            self.x,
            self.y,
            self.amadeusium,
            self.hole)

    def has_ore(self):
        if self.amadeusium == '?':
            return ORE_UNKNOW
        elif int(self.amadeusium) > 0 :
            return AMADEUSIUM
        else:
            return NONE

    def has_hole(self):
        #print("has_hole i {} j {} amadeusium {} hole {}".format(
        #    self.x,
        #    self.y,
        #    self.amadeusium,
        #    self.hole), file=sys.stderr)
        return self.hole

    def update(self, amadeusium, hole):
        self.amadeusium = amadeusium
        self.hole = hole

class CellInfo:
    def __init__(self):
        self.next_amadeusium = -1
        self.next_hole = 0
        self.already_dig = 0
        self.my_trap = 0
        self.my_radar = 0
        self.has_opponent = 0
        self.opponent_trap = 0
        self.opponent_radar = 0


    def __str__(self):
        return '(ore {},hole {} already_dig {} my_trap {} my_radar {} has_oppponent {})'.format(
            self.next_amadeusium,
            self.next_hole,
            self.already_dig,
            self.my_trap,
            self.my_radar,
            self.has_opponent)

    def predict(self, previous):
        self = copy.copy(previous)
        self.already_dig = 0

    def correction(self, cell):
        if cell.amadeusium != '?' :
            self.next_amadeusium = int(cell.amadeusium)
        #if self.next_hole !=

class RobotInfo:
    def __init__(self):
        self.next_x = 0
        self.next_y = 0
        self.next_action = 0
        self.has_dig = 0
        self.has_ore = 0
        self.has_trap = 0
        self.has_radar = 0
        self.status = 0

    def __str__(self):
        return '(next_x {},next_y {},has_dig {}, has_ore {}, has_trap {} has_radar {})'.format(
            self.next_x,
            self.next_y,
            self.has_dig,
            self.has_ore,
            self.has_trap,
            self.has_radar)

    def predict(self,previous):
        self = copy(previous)

    def correction(self, robot):
        self.next_x = robot.x
        self.next_y = robot.y
        if robot.item == AMADEUSIUM:
            self.has_ore = 1
        elif robot.item == TRAP:
            self.has_trap = 1
        elif robot.item == RADAR:
            self.has_radar = 1

class Grid:
    def __init__(self):
        self.cell = []
        for y in range(height):
            for x in range(width):
                self.cell.append(Cell(x, y, 0, 0))
        self.cell_info = []
        for y in range(height):
            for x in range(width):
                self.cell_info.append(CellInfo())
        self.index = 0
        self.size = height * width
        self.find = NONE

    def get_cell(self, x, y):
        if width > x >= 0 and height > y >= 0:
            return self.cell[x + width * y]
        return None

    def get_cell_info(self, x, y):
        if width > x >= 0 and height > y >= 0:
            return self.cell_info[x + width * y]
        return None

    def get_index(self, x, y):
        if width > x >= 0 and height > y >= 0:
            return x + width * y
        return -1


    def get_index_cross(self,x,y):
        # Back
        t_tuple = [-1,-1,-1,-1,-1]
        if width > x - 1 >= 0 and height > y >= 0:
            t_tuple[0] = (x - 1) + width * y
        # Middle
        if width > x > 0 and height > y >= 0:
            t_tuple[1] = x + width * y
        # Front
        if width > x + 1 >= 0 and height > y >= 0:
            t_tuple[4] = (x + 1) + width * y
        # Up
        if width > x > 0 and height > y - 1 >= 0:
            t_tuple[2] = x + width * (y - 1)
        # Down
        if width > x > 0 and height > y + 1 >= 0:
            t_tuple[3] = x + width * (y + 1)
        t_tuple = tuple(t_tuple)
        return t_tuple

    def get_index_square(self,x,y):
        t_true = True
        if width <= x + 2 or x - 2 < 1 or height <= y + 2 or (y - 2) < 0:
            t_true = False
        if t_true == False:
            return None
        #t_tuple = ((x,y-1),(x+1,y),(x-1,y),(x+2,y),(x-2,y),(x,y+1))

        t_tuple = (
            (x+1,y-1),
            (x-1,y),
            (x+1,y+1))

        #t_tuple = (
        #    (x,y-1),
        #    (x-1,y),(x+1,y),
        #    (x,y+1))
        #print('tuple {}'.format(t_tuple))
        t_result = []
        for i in t_tuple:
            (x,y) = i
            t_result.append(x + width * y)
        t_tuple = tuple(t_result)

        return t_tuple

    def get_index_big_square(self,x,y):
        t_true = True
        if width <= x + 2 or x - 2 < 1 or height <= y + 2 or (y - 2) < 0:
            t_true = False
        if t_true == False:
            return None

        #t_tuple = ((x-1,y-2),(x,y-2),(x+1,y-2),
        #    (x-2,y-1),(x-1,y-1),(x,y-1),(x+1,y-1),(x+2,y-1),
        #    (x-2,y),(x-1,y),(x,y),(x+1,y),(x+2,y),
        #    (x-2,y+1),(x-1,y+1),(x,y+1),(x+1,y+1),(x+2,y+1),
        #    (x-1,y+2),(x,y+2),(x+1,y+2),)

        t_tuple = (
            (x-1,y-1),(x,y-1),(x+1,y-1),
            (x-2,y),(x-1,y),(x+1,y),(x+2,y),
            (x-1,y+1),(x,y+1),(x+1,y+1))

        #t_tuple = (
        #    (x-1,y-1),(x,y-1),(x+1,y-1),
        #    (x-1,y),(x+1,y),
        #    (x-1,y+1),(x,y+1),(x+1,y+1))


        #t_tuple = ((x-2,y-2),(x-1,y-2),(x,y-2),(x+1,y-2),(x+2,y-2),
        #t_tuple = ((x-2,y-1),(x-1,y-1),(x,y-1),(x+1,y-1),(x+2,y-1),
        #    (x-2,y),(x-1,y),(x,y),(x+1,y),(x+2,y),
        #    (x-2,y+1),(x-1,y+1),(x,y+1),(x+1,y+1),(x+2,y+1))
        #    (x-2,y+2),(x-1,y+2),(x,y+2),(x+1,y+2),(x+2,y+2))

        #print('tuple {}'.format(t_tuple))
        t_result = []
        for i in t_tuple:
            (x,y) = i
            t_result.append(x + width * y)
        t_tuple = tuple(t_result)

        return t_tuple


    def return_no_hole(self, agent, agent_info):
        x = agent.x
        y = agent.y
        t_tuple = self.get_index_cross(x,y)

        #print('agent {}'.format(agent), file=sys.stderr)
        #print('t_tuple {}'.format(t_tuple), file=sys.stderr)
        for i in t_tuple :
            test_x = i % width
            test_y = (i - test_x) / width
            #print('{} test_x {} test_y {}'.format(i, test_x, test_y), file=sys.stderr)
            if i == -1 :
                continue

            if self.cell[i].has_ore() == ORE_UNKNOW and self.cell[i].has_hole() != HOLE :
                keep = (0, self.cell[i], self.cell_info[i])
                #print('keep {}'.format(keep), file=sys.stderr)
                return keep
        return None

    def __getitem__(self,index):
        if index < 0 or index >= height * width:
            return None
        return (self.cell[index], self.cell_info[index])

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        has_find = 0
        while  self.index <= self.size:

            if self.index == self.size:
                raise StopIteration

            item_cell = self.cell[self.index]
            item_cell_info = self.cell_info[self.index]

            index = self.index
            self.index = self.index + 1

            x = index % width
            y = math.trunc((index - x) / width)

            if self.find == INIT :
                has_find = 1
                break

            if x == 0 :
                continue

            if item_cell_info.has_opponent == 1 :
                continue


            if self.find == AMADEUSIUM :
                if item_cell.has_ore() == AMADEUSIUM :
                    #if item_cell_info.has_opponent == 1 and int(item_cell.amadeusium) > 1 :
                    #    item_cell_info.has_opponent = 0

                    #if item_cell_info.has_opponent == 1 :
                    #    continue

                    #if int(item_cell.amadeusium) - item_cell_info.already_dig < 0 :
                    #    continue

                    #if item_cell_info.already_dig > 0 and item_cell.has_hole == HOLE :
                    #    continue

                    #print('search amadesium item {} has_ore {}'.format(item_cell,item_cell.has_ore()), file=sys.stderr)
                    has_find = 1
                    break

            elif self.find == PREDICT_AMADEUSIUM :
                if item_cell_info.next_amadeusium > 0 :
                    if item_cell_info.already_dig > 0 :
                        continue

                    has_find = 1
                    break

            elif self.find == NEED_RADAR :


                has_found = True

                #if item_cell.has_ore() == AMADEUSIUM or item_cell.has_hole() == HOLE :
                if item_cell.has_hole() == HOLE :
                    has_found = False

                t_tuple = self.get_index_square(x,y)
                if t_tuple is None:
                    continue

                for i in t_tuple:
                    #print('i {} has_ore {}'.format(i,self.cell[i].has_ore()))
                    if self.cell[i].has_ore() != ORE_UNKNOW or self.cell[i].has_hole() == HOLE:
                        has_found = False
                if has_found == True :
                    has_find = 1
                    break

            elif self.find == NEED_BIG_RADAR :

                #if item_cell.has_ore() != AMADEUSIUM and item_cell_info.next_amadeusium == 0 and item_cell.has_hole() != HOLE :
                #    has_found = False

                has_found = True

                #if item_cell.has_ore() == AMADEUSIUM and item_cell.has_hole() == HOLE :
                if item_cell.has_hole() == HOLE :
                    has_found = False

                t_tuple = self.get_index_big_square(x,y)
                if t_tuple is None:
                    continue

                for i in t_tuple:
                    #print('i {} has_ore {}'.format(i,self.cell[i].has_ore()))
                    if self.cell[i].has_ore() != ORE_UNKNOW or self.cell[i].has_hole() == HOLE:
                        has_found = False
                if has_found == True :
                    has_find = 1
                    break


            elif self.find == NEED_NO_HOLE :
                if item_cell.has_hole() != HOLE and item_cell.has_ore() == ORE_UNKNOW:
                    if item_cell_info.already_dig == 1 :
                        continue

                    has_find = 1
                    break

        if has_find == 0 :
            #print('not found {}'.format(self.find), file=sys.stderr)
            return None
        return (item_cell, item_cell_info)

class GridState:
    def __init__(self):
        self.grid = []
        self.index = 0
        self.start = 0
        self.size = 0

    def append(self, Grid):
        self.grid.append(Grid)
        self.size = self.size + 1

    def pop(self):
        self.size = self.size - 1
        self.start = self.start + 1
        self.grid.pop()

    def previous(self):
        return self[-2]

    def current(self):
        return self[-1]

    def __iter__(self):
        self.index = self.start
        return self

    def __next__(self):
        if self.index == self.size:
            raise StopIteration
        item_grid = self.grid[self.index]
        self.index = self.index + 1
        return item_grid

    def __getitem__(self,index):
        item_grid = self.grid[index]
        return item_grid

class RobotState:
    def __init__(self):
        self.robot = []
        self.robot_info = []
        self.index = 0
        self.size = 0
        self.start = 0

    def append(self, Robot, RobotInfo):
        self.robot.append(copy.copy(Robot))
        self.robot_info.append(copy.copy(RobotInfo))
        self.size = self.size + 1

    def pop(self):
        self.size = self.size - 1
        self.start = self.start + 1
        self.robot.pop()
        self.robot_info.pop()

    def previous(self):
        return self[-2]

    def current(self):
        return self[-1]

    def __iter__(self):
        self.index = self.start
        return self

    def __next__(self):
        if self.index == self.size:
            raise StopIteration
        (robot, robot_info) = (self.robot[self.index], self.robot_info[self.index])
        self.index = self.index + 1
        return (robot,robot_info)

    def __getitem__(self,index):
        (robot, robot_info) = (self.robot[index], self.robot_info[index])
        return (robot,robot_info)

class Game:
    def __init__(self):
        self.grid = Grid()
        self.my_score = 0
        self.enemy_score = 0
        self.radar_cooldown = 0
        self.trap_cooldown = 0
        self.radars = []
        self.traps = []
        self.my_robots = []
        self.enemy_robots = []

    def reset(self):
        self.radars = []
        self.traps = []
        self.my_robots = []
        self.enemy_robots = []

class Strategy():
    def __init__(self, GridState):
        self.index = 0
        self.size = width * height
        self.grid_state = GridState
        self.robot_state = None
        self.find_ore = False
        self.find_surely_ore = False
        self.find_correct_place_radar = False

        self.previous_grid = self.grid_state[-2]
        self.current_grid = self.grid_state[-1]
        self.previous_agent = None
        self.current_agent = None

        self.radar_cooldown = 100
        self.trap_cooldown = 100

        self.previous_grid.find = INIT
        self.current_grid.find = INIT


        for (cell,cell_info) in self.current_grid:
            pass

        for (cell,cell_info) in self.previous_grid:
            pass


        current_grid_iter = iter(self.current_grid)
        for (cell,cell_info) in self.previous_grid:
            (current_cell, current_cell_info) = next(current_grid_iter)
            current_cell_info.predict(cell_info)
            current_cell_info.correction(current_cell)

    def reset(self, RobotState):
        self.robot_state = RobotState
        self.previous_agent = self.robot_state[-2]
        self.current_agent = self.robot_state[-1]


    def find_amadeusium(self):
        self.current_grid.find = AMADEUSIUM
        min_distance = 100
        distance = 0
        keep = None
        (robot,robot_info) = self.current_agent
        for (cell,cell_info) in self.current_grid:
            distance = robot.distance(cell)
            if distance < min_distance:
                min_distance = distance
                keep = (min_distance,cell,cell_info)
        #print('find_amadeusium min_distance {} robot {} keep {}'.format(min_distance,robot, keep), file=sys.stderr)
        return keep

    def find_amadeusium_from_predict(self):
        self.current_grid.find = PREDICT_AMADEUSIUM
        min_distance = 100
        distance = 0
        keep = None
        (robot,robot_info) = self.current_agent
        for (cell,cell_info) in self.current_grid:
            distance = robot.distance(cell)
            if distance < min_distance:
                min_distance = distance
                keep = (min_distance,cell,cell_info)
        return keep

    def find_radar_correct_place(self):
        self.current_grid.find = NEED_RADAR
        min_distance = 100
        distance = 0
        keep = None
        (robot,robot_info) = self.current_agent
        for (cell,cell_info) in self.current_grid:
            distance = robot.distance(cell)
            if distance < min_distance:
                min_distance = distance
                keep = (min_distance,cell,cell_info)
        return keep

    def find_big_radar_correct_place(self):
        self.current_grid.find = NEED_BIG_RADAR
        min_distance = 100
        distance = 0
        keep = None
        (robot,robot_info) = self.current_agent
        for (cell,cell_info) in self.current_grid:
            distance = robot.distance(cell)
            if distance < min_distance:
                min_distance = distance
                keep = (min_distance,cell,cell_info)
        return keep

    def find_no_hole(self):
        self.current_grid.find = NEED_NO_HOLE
        min_distance = 100
        distance = 0
        keep = None
        (robot,robot_info) = self.current_agent
        for (cell,cell_info) in self.current_grid:
            distance = robot.distance(cell)
            #if distance <= 1 :
            #    print('cell {} cell_info {}'.format(cell, cell_info), file=sys.stderr)
            #    print('this no hole seem fine d {} cell {} robot {}'.format(distance,cell, robot), file=sys.stderr)
            if distance < min_distance:
                min_distance = distance
                keep = (min_distance,cell,cell_info)
        #print('find_no_hole min_distance {} robot {} '.format(min_distance,robot), file=sys.stderr)
        return keep

class GameState:
    def __init__(self):
        self.grid_state = GridState()
        self.radars = {}
        self.traps = {}

grid_state = GridState()
robot_state = []
robot_state.append(RobotState())
robot_state.append(RobotState())
robot_state.append(RobotState())
robot_state.append(RobotState())
robot_state.append(RobotState())

opponent_state = []
opponent_state.append(RobotState())
opponent_state.append(RobotState())
opponent_state.append(RobotState())
opponent_state.append(RobotState())
opponent_state.append(RobotState())

grid = Grid()

robot = []
robot_info = []

robot_state[0].append(Robot(0,0,0,0,-1), RobotInfo())
robot_state[1].append(Robot(0,0,0,0,-1), RobotInfo())
robot_state[2].append(Robot(0,0,0,0,-1), RobotInfo())
robot_state[3].append(Robot(0,0,0,0,-1), RobotInfo())
robot_state[4].append(Robot(0,0,0,0,-1), RobotInfo())

opponent_state[0].append(Robot(0,0,0,0,-1), RobotInfo())
opponent_state[1].append(Robot(0,0,0,0,-1), RobotInfo())
opponent_state[2].append(Robot(0,0,0,0,-1), RobotInfo())
opponent_state[3].append(Robot(0,0,0,0,-1), RobotInfo())
opponent_state[4].append(Robot(0,0,0,0,-1), RobotInfo())

grid_state.append(grid)

game = Game()
game_state = GameState()

first_turn = True
turn = 0

# game loop
while True:
    # my_score: Players score
    game.my_score, game.enemy_score = [int(i) for i in input().split()]
    for i in range(height):
        inputs = input().split()
        for j in range(width):
            # amadeusium: amount of amadeusium or "?" if unknown
            # hole: 1 if cell has a hole
            amadeusium = inputs[2 * j]
            hole = int(inputs[2 * j + 1])
            game.grid.get_cell(j, i).update(amadeusium, hole)


    # entity_count: number of entities visible to you
    # radar_cooldown: turns left until a new radar can be requested
    # trap_cooldown: turns left until a new trap can be requested
    entity_count, game.radar_cooldown, game.trap_cooldown = [int(i) for i in input().split()]

    game.reset()
    grid_state.append(game.grid)

    strategy = Strategy(grid_state)

    radar_busy = 0
    trap_busy =0
    radar_i = 0

    for i in range(entity_count):
        #radar_busy = 0
        trap_busy = 0
        radar_i = 0

        # id: unique id of the entity
        # type: 0 for your robot, 1 for other robot, 2 for radar, 3 for trap
        # y: position of the entity
        # item: if this entity is a robot, the item it is carrying (-1 for NONE, 2 for RADAR, 3 for TRAP, 4 for AMADEUSIUM)
        id, type, x, y, item = [int(j) for j in input().split()]

        if type == ROBOT_ALLY:
            if i <= 4 :
                jM = i
            else :
                jM = i - 5

            robot_state[jM].append(Robot(x, y, type, id, item), RobotInfo())
            if item == RADAR :
                #radar_busy = 1
                radar_i = i

        elif type == ROBOT_ENEMY:
            if i <= 4 :
                jO = i
            else :
                jO = i - 5

            opponent_state[jO].append(Robot(x, y, type, id, item), RobotInfo())

            (previous_opponent, previous_opponent_info) = opponent_state[i-5].previous()

            if x == 0 and previous_opponent_info.status == HOME :
                (opponent, opponent_info) = opponent_state[jO].current()
                opponent_info.status = WAITING

            elif x == 0 and previous_opponent_info.status != WAITING :
                (opponent, opponent_info) = opponent_state[jO].current()
                opponent_info.status = HOME

            if x != 0 and previous_opponent_info.status == WAITING :
                (opponent, opponent_info) = opponent_state[jO].current()
                opponent_info.status = DANGEROUS
                previous_opponent_info.status = DANGEROUS

            if x != 0 and previous_opponent_info.status == HOME :
                (opponent, opponent_info) = opponent_state[jO].current()
                opponent_info.status = 0

            if x != 0 and previous_opponent_info.status == DANGEROUS :
                (opponent, opponent_info) = opponent_state[jO].current()
                opponent_info.status = DANGEROUS

                state_info = strategy.current_grid.get_cell_info(x, y)

                state = strategy.current_grid.get_cell(x, y)
                state_front = None
                state_up = None
                state_down = None
                if x + 1 != 30 :
                    state_front = strategy.current_grid.get_cell(x+1, y)
                if y - 1 != -1 :
                    state_up = strategy.current_grid.get_cell(x, y-1)
                if y + 1 != 15 :
                    state_down = strategy.current_grid.get_cell(x, y-1)

                #if state.has_ore() == AMADEUSIUM :
                #    state_info.has_opponent = 1
                #if state_front is not None and state_front.has_ore() == AMADEUSIUM :
                #    if int(state_front.amadeusium) > 1 :
                #        state_info = strategy.current_grid.get_cell_info(x+1, y)
                #        state_info.has_opponent = 1
                if state_front is not None and state_front.has_ore() != NONE :
                    state_info = strategy.current_grid.get_cell_info(x+1, y)
                    state_info.has_opponent = 1
                #elif state_up is not None and state_up.has_ore() == AMADEUSIUM :
                #    state_info = strategy.current_grid.get_cell_info(x, y-1)
                #    state_info.has_opponent = 1
                #elif state_down is not None and state_down.has_ore() == AMADEUSIUM :
                #    state_info = strategy.current_grid.get_cell_info(x, y+1)
                #    state_info.has_opponent = 1


        elif type == TRAP:
            game.traps.append(Entity(x, y, type, id))
            state_info = strategy.current_grid.get_cell_info(x, y)
            state_info.has_opponent = 1

        elif type == RADAR:
            game.radars.append(Entity(x, y, type, id))

    for i in range(len(robot_state)):
        #radar_busy = 0
        radar_need_find = 0
        #print("robot {}".format(i), file=sys.stderr)
        action = 0


        strategy.reset(robot_state[i])

        strategy.radar_cooldown = game.radar_cooldown
        strategy.trap_cooldown = game.trap_cooldown

        (agent, agent_state) = robot_state[i].current()
        (previous_agent, previous_agent_state) = robot_state[i].previous()
        #print('agent {}'.format(agent), file=sys.stderr)
        if agent.x == -1 or agent.y == -1:
            agent.wait("DELETE")
            action = 2
            continue

        #if agent.item == RADAR :
        #    action = 3
        #    agent_state.next_x = previous_agent_state.next_x
        #    agent_state.next_y = previous_agent_state.next_y
        #    state_info = strategy.current_grid.get_cell_info(agent_state.next_x, agent_state.next_y)
        #    #if state_info.has_hole() == HOLE:
        #    if state_info.has_opponent == 1 :
        #        action = 0
        #        #radar_need_find = 1
        #    else :
        #        agent.dig(agent_state.next_x, agent_state.next_y,"")
        #        continue

        if agent.item == AMADEUSIUM :
            action = 1
            agent.move(0, agent.y,"")
            continue

        if previous_agent_state.next_action == 3 and agent.item != RADAR :
            state_info = strategy.current_grid.get_cell(agent_state.next_x, agent_state.next_y)
            pos = Pos(agent_state.next_x, agent_state.next_y)
            distance = agent.distance(pos)
            if distance <= 4 and state_info.has_ore() == AMADEUSIUM :
                agent_state.next_x = previous_agent_state.next_x
                agent_state.next_y = previous_agent_state.next_y
                agent_state.next_action = previous_agent_state.next_action
                agent.dig(agent_state.next_x, agent_state.next_y,"")
                continue

        #elif previous_agent_state.next_action == 3 and agent.item == RADAR :
        #    state_info = strategy.current_grid.get_cell(agent_state.next_x, agent_state.next_y)
        #    pos = Pos(agent_state.next_x, agent_state.next_y)
        #    distance = agent.distance(pos)
        #    if distance <= 4 and state_info.has_ore() == AMADEUSIUM :
        #        agent_state.next_x = previous_agent_state.next_x
        #        agent_state.next_y = previous_agent_state.next_y
        #        agent_state.next_action = previous_agent_state.next_action
        #        agent.dig(agent_state.next_x, agent_state.next_y,"")
        #        continue

        to_do = True
        if first_turn == True:
            pos = Pos(0,7)
            distance = agent.distance(pos)
            if distance > 2 :
                to_do = False
            elif radar_busy == 1 :
                to_do = False
            else :
                action = 4
                radar_busy = 1


        array_result = []
        result = None
        #if action == 0 and to_do == True :
        #    result = strategy.find_big_radar_correct_place()
        if action == 0 and to_do == True and agent.item == RADAR :
            result = strategy.find_big_radar_correct_place()
        if result is not None and action == 0:

            #if x == 0 and game.radar_cooldown == 0 :
            #    radar_busy = 1
            #    action = 4
            #    (d,cell,cell_info) = result
            #    agent_state.next_x = cell.x
            #    agent_state.next_y = cell.y
            #    array_result.append(result)

            #if agent.item == RADAR :
            #    action = 3
            #    (d,cell,cell_info) = result
            #    array_result.append(result)
            action = 3
            (d,cell,cell_info) = result
            agent_state.next_action = 3
            agent_state.next_x = cell.x
            agent_state.next_y = cell.y
            array_result.append(result)



        result = None
        #if action == 0 and to_do == True :
        #    result = strategy.find_radar_correct_place()

        if action == 0 and to_do == True and agent.item == RADAR :
            result = strategy.find_radar_correct_place()
        if result is not None and action == 0:

            #if radar_busy == 0 and game.radar_cooldown == 0 :
            #    radar_busy = 1
            #    action = 4
            #    (d,cell,cell_info) = result
            #    array_result.append(result)
            #    agent_state.next_x = cell.x
            #    agent_state.next_y = cell.y

            #if agent.item == RADAR :
            #    action = 3
            #    (d,cell,cell_info) = result
            #    array_result.append(result)

            action = 3
            (d,cell,cell_info) = result
            agent_state.next_action = 3
            agent_state.next_x = cell.x
            agent_state.next_y = cell.y
            array_result.append(result)



        result = None
        if action == 0 and to_do == True :
            result = strategy.find_amadeusium()
        if result is not None and action == 0:
            action = 3
            (d,cell,cell_info) = result
            array_result.append(result)
            #print("i {} find_amadeusium_from_predict : action {} result {}".format(i, action, cell), file=sys.stderr)


        result = None
        if action == 0 and to_do == True :
            result = strategy.find_amadeusium_from_predict()
        if result is not None and action == 0 :
            action = 3
            (d,cell,cell_info) = result
            array_result.append(result)
            #print("find_amadeusium_from_predict : action {} result {}".format(action, cell), file=sys.stderr)

                #print("request radar: action {} result {}".format(action, cell), file=sys.stderr)

        #if radar_need_find == 1 :
        #    result = strategy.find_radar_correct_place()
        #if result is not None :
        #    action = 3
        #    (d,cell,cell_info) = result
        #    agent_state.next_x = cell.x
        #    agent_state.next_y = cell.y
        #    array_result.append(result)
        #    radar_need_find = 0

        #if x == 0 and radar_busy == 0 and game.radar_cooldown == 0 :
        #    action = 4
        #    radar_busy = 1

        #if x == 0 and action == 0 and trap_busy == 0 and game.trap_cooldown == 0 :
        #    action = 5
        #    trap_busy = 1

        #if x == 0 and to_do == True and radar_busy == 0 and game.radar_cooldown == 0 :
        if agent.x == 0 and to_do == True and radar_busy == 0 and game.radar_cooldown == 0 :

            if turn <= 60 :
                action = 4
                radar_busy = 1
            elif action == 0 :
                action = 4
                radar_busy = 1


        result = None
        #if action == 0 :
        #    result = strategy.find_no_hole()
        #if result is not None and action == 0:
        #    action = 3
        #    array_result.append(result)
        #    (d,cell,cell_info) = result
        #    #print("find_no_hole : action {} result {}".format(action, cell), file=sys.stderr)

        if action == 0 :
            result = strategy.current_grid.return_no_hole(agent, agent_state)
        if result is not None and action == 0:
            action = 3
            array_result.append(result)
            (d,cell,cell_info) = result
            #print("find_no_hole : action {} result {}".format(action, cell), file=sys.stderr)

        if action == 0 :
            action = 1
            x = agent.x + 3
            y = agent.y
            cell = strategy.current_grid.get_cell(x,y)
            cell_info = strategy.current_grid.get_cell_info(x, y)
            array_result.append((0,cell,cell_info))

        agent_state.next_action = 0
        if action == 1 :
            (d, block, block_info) = array_result[0]
            agent.move(block.x, block.y,"")

        elif action == 2:
            agent.wait("NOTHING")

        elif action == 3:
            (d, block, block_info) = array_result[0]
            agent_state.next_x = block.x
            agent_state.next_y = block.y
            agent_state.next_action = action
            #print("action == 3 (dig) d {} block {} agent {}".format(d,block,agent),file=sys.stderr)
            agent.dig(block.x, block.y,"")
            state_info = strategy.current_grid.get_cell_info(block.x, block.y)
            state_info.already_dig = state_info.already_dig + 1

        elif action == 4 :
            agent.request(RADAR,"")

        elif action == 5 :
            agent.request(TRAP,"")

    first_turn = False
    turn = turn + 1
    if turn > 5 :
        grid_state.pop()
        robot_state[i].pop()
