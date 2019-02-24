from grid import Grid
import names
import random
# from ai import AI
import collections

class AI:
    def one_square_away(self, xy_agent, xy_target):
        for i in range(-1,1):
            for j in range(-1,1):
                if (xy_agent[0]+i,xy_agent[1]+i) == (xy_target[0], xy_target[1]):
                    return True
        return False
        
    def find_item(self, grid, item):
        agents_with_item = []
        for i in range(grid.size_x):
            for j in range(grid.size_y):
                location_object = grid.get((i,j))
                if isinstance(location_object, Agent):
                    if item in location_object.inventory:
                        agents_with_item.append(location_object)
        return agents_with_item
    def find_point(self, location, current_position):
        dist = lambda x, y: (x[0]-y[0])**2 + (x[1]-y[1])**2
        try:
            ret = min(location, key=lambda co: dist(co, current_position))
            return ret
        except ValueError:
            return current_position

    def bfs(self, grid, agent, start, goal, mating=False, enemy=False):
        queue = collections.deque([[start]])
        seen = set(start)

        while queue:
            path = queue.popleft()
            x, y = path[-1]

            if mating:
                if self.one_square_away((x, y), start):
                    return path
            elif goal == (x, y):
                return path

            if enemy == True:
                for x2, y2 in ((x+1,y), (x-1,y), (x,y+1), (x,y-1)):
                    if 0 <= x2 < (grid.size_x) and 0 <= y2 < (grid.size_y) and (x2, y2) not in seen:
                        queue.append(path + [(x2, y2)])
                        seen.add((x2, y2))
            else:
                for x2, y2 in ((x+1,y), (x-1,y), (x,y+1), (x,y-1)):
                    if 0 <= x2 < (grid.size_x) and 0 <= y2 < (grid.size_y) and agent.is_movement_possible((y2,x2), grid) and (x2, y2) not in seen:
                        queue.append(path + [(x2, y2)])
                        seen.add((x2, y2))
        return path
                    

    def find_direction(self, start, end):
        x = (end[0] - start[0])
        y = (end[1] - start[1])
        return (x,y)

    def find_food(self, grid, agent):
        # find all food
        location = agent.find_all_foods(grid)
        # return nearest food
        return self.find_point(location, agent.position)

    def find_kill(self, grid, enemy):
        location = enemy.find_all_agents(grid)
        return self.find_point(location, enemy.position)

    def find_mate(self, grid, agent):
        location = agent.find_all_compatible_mates(grid, agent.sex)
        return self.find_point(location, agent.position)
                
    def decide_enemy(self, grid, enemy):
        nearest_want = self.find_kill(grid, enemy)
        # print(self.bfs(grid, enemy, enemy.position, nearest_want, enemy=True), enemy.position, nearest_want)
        path = self.bfs(grid, enemy, enemy.position, nearest_want, enemy=True)
        if len(path) == 1:
            return self.find_direction(enemy.position, path[0])
        return self.find_direction(enemy.position, path[1])

    def decide(self, grid, agent):
        try:
            '''
            if agent.hunger < 15 > 3 and "meat" in agent.inventory:
                nearest_want = self.find_item(grid, "seed")
                # if the path is reasonable
                path = self.bfs(grid, agent, agent.position, nearest_want)
                if len(path) < 10:
                    return self.find_direction(agent.position, path)
                else:
                    nearest_want = self.find_food(grid, agent)
                    path = self.bfs(grid, agent, agent.position, nearest_want)[1]
            '''
            if agent.hunger < 5:
                nearest_want = self.find_mate(grid, agent)
                path = self.bfs(grid, agent, agent.position, nearest_want)[1]
            else:
                nearest_want = self.find_food(grid, agent)
                path = self.bfs(grid, agent, agent.position, nearest_want)[1]
        except ValueError:
            return (0,0)
        except IndexError:
            return (0,0)
        return self.find_direction(agent.position, path)

HUNGER_MAX = 20
HUNGER_TICK_RATE = 1


class Observe:
    def find_all_compatible_mates(self, grid, sex):
        compatible_mates = []
        for i in range(grid.size_x):
            for j in range(grid.size_y):
                a = grid.get((i,j))
                if isinstance(a, Agent):
                    if a.sex != sex:
                        compatible_mates.append((i,j))
        return compatible_mates 
        
    def find_all_foods(self, grid):
        foods = []
        for i in range(grid.size_x):
            for j in range(grid.size_y):
                if isinstance(grid.get((i,j)), Edible):
                    foods.append((i,j))
        return foods
    def find_all_agents(self, grid):
        agents = []
        for i in range(grid.size_x):
            for j in range(grid.size_y):
                if isinstance(grid.get((i,j)), Agent):
                    agents.append((i,j))
        return agents


    # check if movement to xy is possible
    def is_movement_possible(self, xy_to, grid):
        try:
            if isinstance(grid.get((xy_to[0], xy_to[1])), (Edible, type(None), type(0))):
                return True
        except IndexError:
            return False
        return False

    def is_full(self, grid):
        for i in range(grid.size_x):
            for j in range(grid.size_y):
                if grid.get((i,j)) is 0:
                    return False
        return True
        

class Reproduction:
    # check adjascent squares for possible mate
    def can_reproduce(self, xy, sex, grid):
        for i in range(-1,1):
            for j in range(-1,1):
                if not i == 0 and j == 0:
                    try:
                        mate = grid.get((xy[0]+i, xy[1]+j))
                        if isinstance(mate, Agent):
                            if mate.sex != sex:
                                # ensure reproduction can only happen once
                                # per mate set per tick
                                mate.mate_lock += 2
                                return True
                    except IndexError:
                        continue
        return False

    def can_eat(self,xy_to, grid):
        try:
            if isinstance(grid.get(xy_to), Edible):
                return True
        except IndexError:
            pass
    
        return False
    def can_kill(self,xy_to, grid):
        try:
            if isinstance(grid.get(xy_to), Agent):
                return True
        except IndexError:
            pass
    
        return False

class Organism(Reproduction, Observe):
    dead = False
    position = []

    def is_dead(self, hunger):
        if hunger == HUNGER_MAX:
            self.dead = True
            return True
        return False

    def spawn(self, grid):
        if self.is_full(grid):
            return False
        x_to = random.randint(0, grid.size_x)
        y_to = random.randint(0, grid.size_y)
        while not self.is_movement_possible((x_to, y_to), grid):
            x_to = random.randint(0, grid.size_x)
            y_to = random.randint(0, grid.size_y)
        self.position = (x_to, y_to)
        return True

class Edible(Organism):
    def __init__(self):
        # decide if edible is plant or not
        self.is_plant = bool(random.getrandbits(1))
        if self.is_plant:
            self.variety = 'p'
        else:
            self.variety = 'a'
    def try_drop(self):
        if random.randint(0, 2) == 1:
            if self.is_plant:
                return 'seed'
            else:
                return 'meat'
    def tick(self):
        pass

    

class Enemy(Organism):
    variety = 'e'
    ai = AI()
    dead = False
    def tick(self, grid):
        if self.dead:
            grid.update(self.position, None)
            return False

        (move_x, move_y) = self.ai.decide_enemy(grid, self)
        (old_x, old_y) = self.position
        move_x += old_x
        move_y += old_y

        self.position = (move_x, move_y)
        grid.update((old_x, old_y), None)
        grid.update(self.position, self)

        return True
        
class Agent(Organism):
    hunger = 0
    variety = 'h'
    mate_lock = 0
    tick_count = 0
    ai = AI()
    dead = False
    birthed = 0
    inventory = []
    def __init__(self):
        if bool(random.getrandbits(1)):
            self.sex = 'm'
        else:
            self.sex = 'f'

    def gen_name(self, parent=None):
        self.name = '{}'.format(names.get_first_name())
        if parent:
            of = ['of', 'de', 'di']
            self.name += ' {} {}'.format(of[random.randint(0,len(of)-1)], parent.name)
            # print('{} is born'.format(self.name))

    def killed(self):
        dead = True
        # print('{} killed after {} ticks and having birthed {} spawn'.format(self.name, self.tick_count, self.birthed))

    def try_trade(self, xy_to, grid, agent):
        for i in range(-1, 1):
            for j in range(-1, 1):
                if i == 0 and j == 0:
                    continue
                trader = grid.get(xy_to)
                if isinstance(trader, Agent):
                    cont = True
                    for a in range(0,1):
                        if cont == True:
                            for b in range(0,1):
                                if cont == True:
                                    item_a = item_b = None
                                    if a:
                                        grab_a = 'seed'
                                    else:
                                        grab_a = 'meat'
                                    if b:
                                        grab_b = 'seed'
                                    else:
                                        grab_b = 'meat'

                                    for it in range(len(agent.inventory)):
                                        if agent.inventory[it] == grab_a:
                                            item_a = agent.inventory.pop(it)
                                            break
                                    for it in range(len(trader.inventory)):
                                        if trader.inventory[it] == grab_b:
                                            item_b = trader.inventory.pop(it)
                                            break
                                    if item_a and item_b:
                                        print('exchanged {} and {}'.format(item_a, item_b))
                                        cont = False

    def tick(self, grid):
        reproduce = False
        if self.dead:
            return (False, False, False)
        if self.is_dead(self.hunger):
            grid.update(self.position, None)
            return (False, False, False)

        if self.is_full(grid):
            return (False, False, True)

        (move_x, move_y) = self.ai.decide(grid, self)
        (old_x, old_y) = self.position
        move_x += old_x
        move_y += old_y

        if self.can_reproduce(
                (move_x, move_y), self.sex, grid) and not self.mate_lock:
            mate_lock = 2
            reproduce = True
            self.birthed += 1

        self.try_trade((move_x, move_y), grid, self)
        
        if self.can_eat((move_x, move_y), grid):
            edible = grid.get((move_x, move_y))
            drop = edible.try_drop()
            if drop:
                self.inventory.append(drop)
                # print('{} picked up {}'.format(self.name, drop))
            
        self.position = (move_x, move_y)
        grid.update((old_x, old_y), None)
        grid.update(self.position, self)

        if self.mate_lock:
            self.mate_lock -= 1
        self.hunger += 1
        self.tick_count+=1
        return (True, reproduce, False)
