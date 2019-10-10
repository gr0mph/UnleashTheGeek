import sys
import math
from random import *

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

class Pos:
    def __init__(self, x, y):
        self.x = x
        self.y = y

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
        print("has_hole i {} j {} amadeusium {} hole {}".format(
            self.x,
            self.y,
            self.amadeusium,
            self.hole), file=sys.stderr)
        return self.hole

    def update(self, amadeusium, hole):
        self.amadeusium = amadeusium
        self.hole = hole

class CellInfo:
    def __init__(self):
        self.next_amadeusium = '?'
        self.next_hole = 0
        self.my_trap = 0
        self.my_radar = 0
        self.has_opponent = 0
        self.opponent_trap = 0
        self.opponent_radar = 0


    def __str__(self):
        return '(ore {},hole {},trap {}, radar {}, opponent {})'.format(
            self.next_amadeusium,
            self.next_hole,
            self.trap,
            self.radar,
            self.has_opponent)

    def predict(self, previous):
        self = copy(previous)

    def correction(self, cell):
        if cell.amadeusium != '?' :
            self.next_amadeusium = self.amadeusium

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
        t_tuple = [-1,-1,-1,-1]
        if width > x - 1 >= 0 and height > y >= 0:
            t_tuple[3] = x - 1 + width * y
        # Front
        if width > x + 1 >= 0 and height > y >= 0:
            t_tuple[0] = x - 1 + width * y
        # Up
        if width > x >= 0 and height > y - 1 >= 0:
            t_tuple[1] = x + width * (y - 1)
        # Down
        if width > x >= 0 and height > y + 1 >= 0:
            t_tuple[2] = x + width * (y + 1)
        t_tuple = tuple(t_tuple)
        return t_tuple

    def get_index_square(self,x,y):
        t_true = True
        if width > x + 1 > x - 1 >= 0 and height > y + 1 > y - 1 >= 0:
            t_true = False
        if t_true == False:
            return None
        t_tuple = ((x-1,y-1),(x,y-1),(x+1,y-1),(x-1,y),(x,y),(x+1,y),(x-1,y+1),(x,y+1),(x+1,y+1))
        t_result = []
        for i in t_tuple:
            (x,y) = i
            t_result.append(x + width * y)
        t_tuple = tuple(t_result)
        return t_tuple

    def __getitem__(self,index):
        if index < 0 or index >= height * wight:
            return None
        return (self.cell[index], self.cell_info[index])

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index == self.size:
            raise StopIteration

        while True:
            item_cell = self.cell[self.index]
            item_cell_info = self.cell_info[self.index]
            self.index = self.index + 1

            if self.find == ORE and item_cell.has_ore() > 0 :
                break


        return (item_cell, item_cell_info)

class GridState:
    def __init__(self):
        self.grid = []
        self.index = 0
        self.size = 0

    def append(self, Grid):
        self.grid.append(Grid)
        self.size = self.size + 1

    def previous(self):
        return self[-2]

    def current(self):
        return self[-1]

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index == self.size:
            raise StopIteration
        item_grid = self.grid[self.index]
        self.index = self.index + 1
        return item_grid

    def __getitem__(self,index):
        item_grid = self.grid[self.index]
        return item_grid


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

class RobotState:
    def __init__(self):
        self.queue = []
        self.index = 0
        self.size = 0
        self.min_x = 0
        self.next_x = 0
        self.next_y = 0
        self.wait = 0
        self.has_dig = 0


    def append(self, Robot):
        self.queue.append(Robot)
        self.size = self.size + 1


    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index == self.size:
            raise StopIteration
        item = self.queue[self.index]
        self.index = self.index + 1
        return item

    def __getitem__(self,index):
        if( abs(index) > self.index ):
            return self.queue[-1]
        return self.queue[index]

    def __setitem__(self,index,value):
        self.queue[index] = value

    def match(self, Robot):
        if self.size == 0:
            return True

        if self.queue[-1].id != Robot.id:
            return False
        #if self.queue[-1].next_x != Robot.x:
        #    return False
        if self.next_y != Robot.y:
            return False

        return True


class Strategy():
    def __init__(self, Grid, Pos):
        self.index = 0
        self.size = width * height
        self.grid_state = GridState
        self.pos = Pos
        self.find_ore = False
        self.find_surely_ore = False
        self.find_correct_place_radar = False

    def find_amadeusium(self):
        grid.find = ORE
        min_distance = 100
        keep = None
        for (cell,cell_info) in Grid:
            distance = distance(self.pos,cell)
            if distance < min_distance:
                min_distance = distance
                keep = (cell,cell_info)
        return keep

    def find_amadeusium_from_predict(self):

        return (0,0)

    def find_radar_correct_place(self):

        return (0,0)

class GameState:
    def __init__(self):
        self.grid_state = GridState()
        self.radars = {}
        self.traps = {}
        self.my_robots = {}
        self.my_robots[0] = RobotState()
        self.my_robots[1] = RobotState()
        self.my_robots[2] = RobotState()
        self.my_robots[3] = RobotState()
        self.my_robots[4] = RobotState()

        self.en_robots = {}
        self.en_robots[0] = RobotState()
        self.en_robots[1] = RobotState()
        self.en_robots[2] = RobotState()
        self.en_robots[3] = RobotState()
        self.en_robots[4] = RobotState()

game = Game()
game_state = GameState()
radar_count = 6
radar_x = (5,9,13,17,21,25,5,13,21)
radar_y = (4,9,4,9,4,9,14,14,14)
radar_busy = 0

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
    game_state.grid_state.append(game.grid)

    grid_previous = game_state.grid_state.previous()
    grid_current  = game_state.grid_state.current()


    for i in range(entity_count):
        # id: unique id of the entity
        # type: 0 for your robot, 1 for other robot, 2 for radar, 3 for trap
        # y: position of the entity
        # item: if this entity is a robot, the item it is carrying (-1 for NONE, 2 for RADAR, 3 for TRAP, 4 for AMADEUSIUM)
        id, type, x, y, item = [int(j) for j in input().split()]

        if type == ROBOT_ALLY:
            game.my_robots.append(Robot(x, y, type, id, item))
        elif type == ROBOT_ENEMY:
            game.enemy_robots.append(Robot(x, y, type, id, item))
        elif type == TRAP:
            game.traps.append(Entity(x, y, type, id))
        elif type == RADAR:
            game.radars.append(Entity(x, y, type, id))

    print("global entity {} radar {} trap {}".format(
        entity_count,
        game.radar_cooldown,
        game.trap_cooldown), file=sys.stderr)

    j = 0
    trap_busy = 0
    for i in range(len(game.my_robots)):
        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr)

        # WAIT|
        # MOVE x y|REQUEST item
        #game.my_robots[i].wait(f"Starter AI {i}")
        x = game.my_robots[i].x
        y = game.my_robots[i].y


        #while game_state.my_robots[j].match(game.my_robots[i]) == False:
        #    j = j + 1

        game_state.my_robots[j].append(game.my_robots[i])

        if x == -1 or y == -1:
            j = j + 1
            game.my_robots[i].wait("DELETE")
            continue

        if x == 0:
            game_state.my_robots[j].has_dig = 0
            game_state.my_robots[j].wait = 0

        if i == 2 and radar_count >= 0 and x == 0 :
            if game.radar_cooldown == 0 and radar_busy == 0 :
                radar_busy = 1
                radar_count = radar_count - 1
                game.my_robots[i].request(RADAR, "")
                j = j + 1
                continue

        if radar_count < 0 and x == 0 :
            if radar_count == 0 :
                radar_count = radar_count - 1
            if game.radar_cooldown == 0 and radar_busy == 0 :
                radar_busy = 1
                game.my_robots[i].request(RADAR, "")
                j = j + 1
                continue

        #if radar_count == 0 and x == 0 :
        #    if game.trap_cooldown == 0 and trap_busy == 0 :
        #        trap_busy = 1
        #        game.my_robots[i].request(TRAP, "")
        #        j = j + 1
        #        continue


        cell = game.grid.get_cell(x,y)
        cell_back = game.grid.get_cell(x-1,y)
        cell_up = game.grid.get_cell(x,y-1)
        cell_down = game.grid.get_cell(x,y+1)
        cell_front = game.grid.get_cell(x+1,y)



        if i == 2 and radar_busy == 1 and radar_count >= 0 :
            if x == radar_x[5-radar_count] and y == radar_y[5-radar_count] :
                game.my_robots[i].dig(x,y, "")
                radar_busy = 0
                j = j + 1
                continue
            else :
                game.my_robots[i].move(radar_x[5-radar_count],radar_y[5-radar_count], "")
                j = j + 1
                continue


        #print("information {} x {} y {} next_x {} next_y {} min_x {} wait {} ".format(
        #    i,
        #    game.my_robots[i].x,
        #    game.my_robots[i].y,
        #    game.my_robots[i].next_x,
        #    game.my_robots[i].next_y,
        #    game.my_robots[i].min_x,
        #    game.my_robots[i].wait), file=sys.stderr)

        previous = game_state.my_robots[j][-2]

        if game.my_robots[i].has_ore() :
            game.my_robots[i].move(0,y, "")
            # Back home 0 {y} {i}

        elif cell.has_ore() == AMADEUSIUM :
            if game_state.my_robots[j].wait != 1 :
                game.my_robots[i].min_x = x
            game.my_robots[i].dig(x,y, "")

        elif cell_back is not None and cell_back.has_ore() == AMADEUSIUM and game_state.my_robots[j].has_dig == 0 :
            game_state.my_robots[j].has_dig = 1
            if game_state.my_robots[j].wait != 1 :
                game.my_robots[i].min_x = x - 1
            game.my_robots[i].dig(x-1,y, "")

        elif cell_up is not None and cell_up.has_ore() == AMADEUSIUM and game_state.my_robots[j].has_dig == 0 :
            game_state.my_robots[j].has_dig = 1
            if game_state.my_robots[j].wait != 1 :
                game.my_robots[i].min_x = x
            game.my_robots[i].dig(x,y-1, "")

        elif cell_down is not None and cell_down.has_ore() == AMADEUSIUM and game_state.my_robots[j].has_dig == 0 :
            game_state.my_robots[j].has_dig = 1
            if game_state.my_robots[j].wait != 1 :
                game.my_robots[i].min_x = x
            game.my_robots[i].dig(x,y+1, "")

        elif cell_front is not None and cell_front.has_ore() == AMADEUSIUM and game_state.my_robots[j].has_dig == 0 :
            game_state.my_robots[j].has_dig = 1
            if game_state.my_robots[j].wait != 1 :
                game.my_robots[i].min_x = x + 1
            game.my_robots[i].dig(x+1,y, "")

        elif game_state.my_robots[j].wait == 1 :
            x = game_state.my_robots[j].next_x = 0
            y = game_state.my_robots[j].next_y
            game.my_robots[i].move(x,y, "{y}")

        elif x < game_state.my_robots[j].min_x :
            x = game_state.my_robots[j].next_x = game_state.my_robots[j].min_x
            y = game_state.my_robots[j].next_y
            game.my_robots[i].move(x,y, "")
            # Back home {game.my_robots[i].min_x} {y} {i}

        elif cell_front is not None and cell_front.has_ore() == ORE_UNKNOW and cell_front.has_hole() != HOLE :
            if cell.has_ore() == ORE_UNKNOW and cell.has_hole() != HOLE and x != 0 :
                game_state.my_robots[j].min_x = x
            elif x < 28 :
                game_state.my_robots[j].min_x = x + 2

            game.my_robots[i].dig(x + 1,y, "")


        elif cell.has_ore() == ORE_UNKNOW and cell.has_hole() != HOLE and x != 0 :
            game_state.my_robots[j].min_x = x
            game.my_robots[i].dig(x,y, "")
            #print("What!",file=sys.stderr)
            # Try get ore {x} {y} {i}

        elif x == 29 or x == 28 :
            game_state.my_robots[j].next_y = randint(0,14)
            while y == game_state.my_robots[j].next_y:
                game_state.my_robots[j].next_y = randint(0,14)

            y = game_state.my_robots[j].next_y
            x = game_state.my_robots[j].next_x = x
            game_state.my_robots[j].min_x = 0
            game_state.my_robots[j].wait = 1
            game.my_robots[i].move(x,y, "Back home")
            # Back home 0 {y} {i}

        else :
            x = game_state.my_robots[j].next_x = (x + 1)
            y = game_state.my_robots[j].next_y = y
            game.my_robots[i].move(x,y, "")
            # Move {x} {y} {i}

        j = j + 1

        if radar_count < 0 :
            radar_busy = 0
