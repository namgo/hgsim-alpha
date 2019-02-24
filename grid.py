from PIL import Image, ImageDraw

WIDTH = 200
HEIGHT = 200

class Grid:
    size = 19
    size_x = size
    size_y = size
    layout = []
   
    def __init__(self):
        self.layout = [[0 for _ in range(self.size_y)] for _ in range(self.size_x)]
    def update(self, location, value):
        self.layout[location[0]][location[1]] = value
    def get(self, location):
        return self.layout[location[0]][location[1]]
        

class GridImage:
    grid = None
    frames = []
    x_coords = list()
    y_coords = list()
    # create the grid to be saved as an image
    def create_grid(self, grid, image, draw):
        y_start = 0
        y_end = image.height
        x_start = 0
        x_end = image.width
        step_size = int(image.width / grid.size)

        for x in range(0, image.width, step_size):
            line = ((x, y_start), (x, y_end))
            self.x_coords.append(x)
            draw.line(line, fill=(128,128,128))

        for y in range(0, image.height, step_size):
            line = ((x_start, y), (x_end, y))
            self.y_coords.append(y)
            draw.line(line, fill=(128,128,128))
    
    # fill a rectangle on the grid
    def fill(self, xy, color, draw):
        draw.rectangle(
            [self.x_coords[xy[0]], self.y_coords[xy[1]], self.x_coords[xy[0]+1], self.y_coords[xy[1]+1]],
            color,
            (128,128,128)
        )
    def fill_by_variety(self, draw, grid):
        for i in range(grid.size_y - 1 ):
            for j in range(grid.size_x - 1):
                try:
                    if grid.layout[i][j].variety is 'a':
                        self.fill([i,j], (255,0,0), draw)
                    elif grid.layout[i][j].variety is 'p':
                        self.fill([i,j], (0,100,0), draw)
                    elif grid.layout[i][j].variety is 'h':
                        self.fill([i,j], (128,128,128), draw)
                    elif grid.layout[i][j].variety is 'e':
                        self.fill([i,j], (0,0,255), draw)
                except AttributeError:
                    self.fill([i,j], (255,255,255), draw)
        
    def append_frame(self, grid):
        # create a new image to save
        image = Image.new(mode='RGB', size=(WIDTH, HEIGHT), color=(255,255,255))
        draw = ImageDraw.Draw(image)

        # initialize the grid
        self.create_grid(grid, image, draw)
        # fill based on what's in it
        self.fill_by_variety(draw, grid)
        self.frames.append(image)
        
    def save_png(self, filename):
        self.frames[len(self.frames)-1].save(filename)
    def save_gif(self, filename):
        self.frames[0].save(filename, format='GIF', append_images=self.frames[1:], save_all=True, duration=100, loop=0)
