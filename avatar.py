import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap
from PIL import Image

EMPTY = 0
WALL = 1
SAND = 2
WOOD = 3
FIRE = 4
SMOKE_DARK = 5
SMOKE_LIGHT = 6

textures = {
    EMPTY: np.array(Image.open("tiles/empty.png").convert("RGB")),
    WALL: np.array(Image.open("tiles/wall.png").convert("RGB")),
    SAND: np.array(Image.open("tiles/sand.png").convert("RGB")),
    WOOD: np.array(Image.open("tiles/wood.png").convert("RGB")),
    FIRE: np.array(Image.open("tiles/fire.png").convert("RGB")),
    SMOKE_DARK: np.array(Image.open("tiles/smoke_dark.png").convert("RGB")),
    SMOKE_LIGHT: np.array(Image.open("tiles/smoke_light.png").convert("RGB"))
}

smoke_life = None

# Function for creating initial 2D state
def create_initial_state(size):
    global smoke_life
    grid = np.random.choice([EMPTY, WALL, SAND, WOOD, FIRE],
                            size=(size, size),
                            p=[0.4, 0.2, 0.1, 0.2, 0.1])

    global smoke_life  # Spremenljivko označi kot globalno
    smoke_life = np.zeros((size, size), dtype=int)

    # Dodeli začetno življenjsko dobo dima
    smoke_life[12, 5] = 20

    # Fixed border
    grid[0, :] = WALL
    grid[:, 0] = WALL
    grid[-1, :] = WALL
    grid[:, -1] = WALL
    return grid

# Function for generating next generation
def generate_next_gen(grid):
    global smoke_life
    new_grid = np.copy(grid)
    rows, cols = grid.shape

    for i in range(rows-2, 0, -1):
        for j in range(1, cols-1):
            if grid[i, j] == WALL:
                continue  # Wall stays in the same place

            if grid[i, j] == SAND:
                # 1. Če je pod peskom prazen prostor, pade naravnost dol
                if i < grid.shape[0] - 1 and grid[i + 1, j] == EMPTY:
                    new_grid[i, j] = EMPTY
                    new_grid[i + 1, j] = SAND

                # 2. Če se ne more premakniti naravnost dol, preveri diagonalno
                else:
                    # 3. Poskusi najprej naključno levo ali desno (daje bolj naraven efekt)
                    directions = [(1, -1), (1, 1)]
                    np.random.shuffle(directions)

                    for di, dj in directions:
                        ni, nj = i + di, j + dj

                        # Preveri, če smo še vedno znotraj mreže
                        if 0 <= ni < grid.shape[0] and 0 <= nj < grid.shape[1]:
                            if grid[ni, nj] == EMPTY:
                                new_grid[i, j] = EMPTY
                                new_grid[ni, nj] = SAND
                                break  # Premik izveden - ne preverjaj več

                    # 4. Če ni nobene možnosti za premik, ostane na mestu
                    else:
                        new_grid[i, j] = SAND




            elif grid[i, j] == WOOD:
                # 1. Fall down if there is space
                if i < rows - 1 and grid[i + 1, j] == EMPTY:  # Check bottom boundary
                    new_grid[i, j] = EMPTY
                    new_grid[i + 1, j] = WOOD

                # 2. Check neighboring cells for fire with safe boundary checks
                if (i > 0 and grid[i - 1, j] == FIRE) or \
                        (i < rows - 1 and grid[i + 1, j] == FIRE) or \
                        (j > 0 and grid[i, j - 1] == FIRE) or \
                        (j < cols - 1 and grid[i, j + 1] == FIRE):
                    new_grid[i, j] = FIRE

            elif grid[i, j] == FIRE:
                # 1. Fire moves only downwards
                if i < rows - 1:  # Check if not at the bottom of the grid
                    if grid[i + 1, j] == EMPTY:
                        new_grid[i, j] = EMPTY
                        new_grid[i + 1, j] = FIRE
                    elif grid[i + 1, j] == WOOD:
                        new_grid[i + 1, j] = FIRE

                    # 2. If there is a flammable element (WOOD) under the fire → Dark smoke
                    elif grid[i + 1, j] == WOOD:
                        new_grid[i, j] = SMOKE_DARK
                        smoke_life[i, j] = 20  # Give smoke an initial lifespan

                    # 3. If there is no flammable element under the fire → Light smoke
                    else:
                        new_grid[i, j] = SMOKE_LIGHT
                        smoke_life[i, j] = 20

            elif grid[i, j] in [SMOKE_DARK, SMOKE_LIGHT]:
                # 1. Decrease smoke lifespan
                smoke_life[i, j] -= 1
                if smoke_life[i, j] <= 0:
                    new_grid[i, j] = EMPTY  # Smoke disappears when lifespan reaches 0
                    continue

                # 2. Smoke tries to move upwards first in any direction (straight, left, right)
                directions = [(-1, 0), (-1, -1), (-1, 1)]  # Up, up-left, up-right
                np.random.shuffle(directions)  # Random direction choice

                moved = False
                for di, dj in directions:
                    ni, nj = i + di, j + dj

                    # Check grid boundaries
                    if ni < 0 or ni >= rows or nj < 0 or nj >= cols:
                        continue  # Avoid errors at grid edges

                    if grid[ni, nj] == EMPTY:
                        new_grid[i, j] = EMPTY
                        new_grid[ni, nj] = grid[i, j]
                        smoke_life[ni, nj] = smoke_life[i, j]
                        moved = True
                        break  # Smoke moves and stops checking

                # 3. If smoke cannot move upwards → Move left or right
                if not moved:
                    if j > 0 and grid[i, j - 1] == EMPTY:  # Left
                        new_grid[i, j] = EMPTY
                        new_grid[i, j - 1] = grid[i, j]
                        smoke_life[i, j - 1] = smoke_life[i, j]
                    elif j < cols - 1 and grid[i, j + 1] == EMPTY:  # Right
                        new_grid[i, j] = EMPTY
                        new_grid[i, j + 1] = grid[i, j]
                        smoke_life[i, j + 1] = smoke_life[i, j]

    return new_grid

# Function to draw the grid with textures
def draw_grid(grid):
    img = np.zeros((grid.shape[0] * 32, grid.shape[1] * 32, 3), dtype=np.uint8)
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            img[i * 32:(i + 1) * 32, j * 32:(j + 1) * 32] = textures[grid[i, j]]
    return img

# Function for animating the simulation
def animate(frame_num, grid, img):
    new_grid = generate_next_gen(grid)
    img.set_data(draw_grid(new_grid))
    grid[:] = new_grid
    return img,


def create_test_environment(size):
    global smoke_life
    grid = np.full((size, size), EMPTY)

    # Dodaj več plasti peska
    grid[5, 4:7] = SAND
    grid[6, 4:7] = SAND
    grid[7, 4:7] = SAND

    # Dodaj les na več mestih
    grid[8, 5] = WOOD
    grid[9, 5] = WOOD
    grid[8, 6] = WOOD
    grid[9, 6] = WOOD

    # Dodaj ogenj ob lesu
    grid[10, 5] = FIRE
    grid[10, 6] = FIRE

    # Dim postavljen na različnih mestih
    grid[12, 5] = SMOKE_DARK
    grid[12, 6] = SMOKE_LIGHT
    grid[13, 4] = SMOKE_LIGHT
    grid[13, 7] = SMOKE_DARK

    # Dodaj stene za ustvarjanje ovir in kanalov
    grid[3, :] = WALL
    grid[:, 3] = WALL
    grid[4:10, 8] = WALL
    grid[5, 2:6] = WALL
    grid[8, 0:3] = WALL
    grid[11, 6:9] = WALL

    # Inicializacija smoke_life
    smoke_life = np.zeros((size, size), dtype=int)

    # Nastavi življenjsko dobo dima
    smoke_life[12, 5] = 20
    smoke_life[12, 6] = 15
    smoke_life[13, 4] = 10
    smoke_life[13, 7] = 18

    return grid


