from grid import Grid, GridImage
from organism import Agent, Edible, Enemy


class Game:
    def __init__(self, grid, grid_image):
        self.grid = grid
        self.grid_image = grid_image

    def spawn(self, organism_obj, num, give_name=False, parent=None):
        organisms = list(range(num))
        for i in range(num):
            organisms[i] = organism_obj()
            organisms[i].spawn(grid)
            if give_name:
                organisms[i].gen_name(parent=parent)
            self.grid.update(organisms[i].position, organisms[i])

        return organisms


    def start(self, num_agents, num_edibles, num_enemies):
        self.agents = self.spawn(Agent, num_agents, give_name=True)
        self.edibles = self.spawn(Edible, num_edibles)
        self.enemies = self.spawn(Enemy, num_enemies)

        return True

    def _tick_enemies(self):
        for i in range(len(self.enemies)):
            self.enemies[i].tick(self.grid)
            self.grid.update(self.enemies[i].position, self.enemies[i])

    def _tick_agents(self):
        all_alive = False
        for i in range(len(self.agents)):
            alive, reproduce, grid_full = self.agents[i].tick(self.grid)
            if alive:
                self.grid.update(self.agents[i].position, self.agents[i])
                all_alive = True
            else:
                self.agents[i].dead = True
                continue

            if reproduce:
                self.agents += self.spawn(Agent, 1, give_name=True, parent=self.agents[i])
        return all_alive

    def tick(self):
        self._tick_enemies()
        all_alive = self._tick_agents()
        self.grid_image.append_frame(self.grid)
        return all_alive
    def play(self):
        count = 0
        tick_count = 0
        while True:
            if not self.tick():
                break
            if count == 10:
                self.edibles += self.spawn(Edible, 10)
                #self.enemies += self.spawn(Enemy, int(self.grid.size/5))
                self.enemies += self.spawn(Enemy, int(self.grid.size/6))
                count = 0
            count += 1
            tick_count += 1
        print(tick_count)

grid = Grid()
grid_image = GridImage()
game = Game(grid, grid_image)
game.start(int(grid.size/2), int(grid.size/1.2), int(grid.size/3))

game.play()

grid_image.save_gif('game.gif')
