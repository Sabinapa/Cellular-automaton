import numpy as np
from PIL import Image

EMPTY = 0
WALL = 1
SAND = 2
WOOD = 3
FIRE = 4
SMOKE_DARK = 5
SMOKE_LIGHT = 6
WATER = 7
ICE = 8

textures = {
    EMPTY: np.array(Image.open("tiles/empty.png").convert("RGB")),
    WALL: np.array(Image.open("tiles/wall.png").convert("RGB")),
    SAND: np.array(Image.open("tiles/sand.png").convert("RGB")),
    WOOD: np.array(Image.open("tiles/wood.png").convert("RGB")),
    FIRE: np.array(Image.open("tiles/fire.png").convert("RGB")),
    SMOKE_DARK: np.array(Image.open("tiles/smoke_dark.png").convert("RGB")),
    SMOKE_LIGHT: np.array(Image.open("tiles/smoke_light.png").convert("RGB")),
    WATER: [
        np.array(Image.open("tiles/light_blue.png").convert("RGB")),
        np.array(Image.open("tiles/medium_blue.png").convert("RGB")),
        np.array(Image.open("tiles/dark_blue.png").convert("RGB")),
        np.array(Image.open("tiles/full_blue.png").convert("RGB")),
    ],
    ICE: np.array(Image.open("tiles/ice.png").convert("RGB"))
}

smoke_life = None
water_amount = None

# Function for creating initial 2D state
def create_initial_state(size):
    global smoke_life, water_amount
    grid = np.random.choice([EMPTY, WALL, SAND, WOOD, FIRE],
                            size=(size, size),
                            p = [0.2, 0.2, 0.2, 0.2, 0.2])

    global smoke_life
    smoke_life = np.zeros((size, size), dtype=int)
    water_amount = np.zeros((size, size), dtype=float)

    # Fixed border
    grid[0, :] = WALL
    grid[:, 0] = WALL
    grid[-1, :] = WALL
    grid[:, -1] = WALL
    return grid

# Function for generating next generation
def generate_next_gen(grid, steps, water_amount):
    global smoke_life
    if smoke_life is None or smoke_life.shape != grid.shape:
        smoke_life = np.zeros_like(grid, dtype=int)

    if water_amount is None or water_amount.shape != grid.shape:
        water_amount = np.zeros_like(grid, dtype=float)

    new_grid = np.copy(grid) # Copy the grid to avoid in-place changes
    rows, cols = grid.shape

    for i in range(rows-2, 0, -1):
        for j in range(1, cols-1):
            if grid[i, j] == WALL:
                continue  # Wall stays in the same place

            if grid[i, j] == SAND:
                # 1. iF there is empty space below, sand falls down
                if i < grid.shape[0] - 1 and grid[i + 1, j] in [EMPTY, WALL, WOOD]: # Check bottom boundary and empty space

                    # Check if the cell below is wall or wood
                    if grid[i + 1, j] == WALL or grid[i + 1, j] == WOOD:
                        new_grid[i, j] = SAND

                    # If the cell below is empty, move sand down
                    elif grid[i + 1, j] == EMPTY:
                        new_grid[i, j] = EMPTY
                        new_grid[i + 1, j] = SAND

                # 2. If there is water below, sand displaces water
                elif i < grid.shape[0] - 1 and grid[i + 1, j] == WATER:
                    moved = False

                    # Try to displace water left/right
                    directions = [(0, -1), (0, 1)]
                    np.random.shuffle(directions)

                    for di, dj in directions:
                        ni, nj = i + 1, j + dj

                        if 0 <= nj < grid.shape[1] and grid[ni, nj] == EMPTY:
                            # Move water left/right
                            new_grid[ni, nj] = WATER
                            new_grid[i + 1, j] = SAND
                            moved = True
                            break  # IF there is no option to move left/right -> Swap places with water

                    # If there is no option to move left/right -> Swap places with water
                    if not moved:
                        new_grid[i, j] = WATER
                        new_grid[i + 1, j] = SAND

                # 3. Check diagonal movement if it cannot move down
                else:
                    directions = [(1, -1), (1, 1)]
                    np.random.shuffle(directions)

                    for di, dj in directions:
                        ni, nj = i + di, j + dj
                        if 0 <= ni < grid.shape[0] and 0 <= nj < grid.shape[1]:
                            if grid[ni, nj] == EMPTY:
                                new_grid[i, j] = EMPTY
                                new_grid[ni, nj] = SAND
                                break

                    # 4. If there is no option to move, stay in place
                    else:
                        new_grid[i, j] = SAND

            elif grid[i, j] == WOOD:

                # 1. Check if wood is under water
                current_i = i
                while current_i > 0 and grid[current_i - 1, j] == WATER:
                    new_grid[current_i - 1, j] = WOOD
                    new_grid[current_i, j] = WATER
                    water_amount[current_i, j] = min(water_amount[current_i, j] + 0.5, 1.0)
                    # Update grid
                    grid[current_i - 1, j] = WOOD
                    grid[current_i, j] = WATER
                    current_i -= 1

                if current_i != i:
                    continue

                # Check if wood is trapped between 75% water cells
                left_water = j > 0 and grid[i, j - 1] == WATER and water_amount[i, j - 1] >= 0.75
                right_water = j < cols - 1 and grid[i, j + 1] == WATER and water_amount[i, j + 1] >= 0.75
                above_empty = i > 0 and grid[i - 1, j] == EMPTY

                if left_water and right_water and above_empty:
                    new_grid[i - 1, j] = WOOD
                    new_grid[i, j] = WATER
                    water_amount[i, j] = min(water_amount[i, j] + 0.5, 1.0)
                    continue

                # 2. Fall down if there is space
                if i < rows - 1 and grid[i + 1, j] == EMPTY:  # Check bottom boundary and empty space
                    new_grid[i, j] = EMPTY
                    new_grid[i + 1, j] = WOOD

                elif i < rows - 1 and grid[i + 1, j] == WATER:  # Check bottom boundary and empty space
                    new_grid[i, j] = WOOD # Wood stays in place

                # 2. Check neighboring cells for fire with safe boundary checks up, down, left, right
                elif (i > 0 and grid[i - 1, j] == FIRE) or \
                        (i < rows - 1 and grid[i + 1, j] == FIRE) or \
                        (j > 0 and grid[i, j - 1] == FIRE) or \
                        (j < cols - 1 and grid[i, j + 1] == FIRE):
                    new_grid[i, j] = FIRE

            elif grid[i, j] == FIRE:
                # 1. Fire moves downwards
                if i < rows - 1:  # Check bottom boundary
                    if grid[i + 1, j] == EMPTY:
                        new_grid[i, j] = EMPTY
                        new_grid[i + 1, j] = FIRE

                    # 2. If flammable element (wood) is below → Dark smoke
                    elif grid[i + 1, j] == WOOD:
                        new_grid[i + 1, j] = FIRE  # Wood burns
                        new_grid[i, j] = SMOKE_DARK  # Fire turns into dark smoke
                        smoke_life[i, j] = 6 #Life span of smoke

                    # 3. If it cannot move downwards → Light smoke
                    else:
                        new_grid[i, j] = SMOKE_LIGHT
                        smoke_life[i, j] = 6

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

                   # Check boundary conditions
                    if ni < 0 or ni >= rows or nj < 0 or nj >= cols:
                        continue  # Avoid errors at grid edges

                    # Check if the cell is empty, if so, move smoke
                    if grid[ni, nj] == EMPTY:
                        new_grid[i, j] = EMPTY
                        new_grid[ni, nj] = grid[i, j]
                        smoke_life[ni, nj] = smoke_life[i, j]
                        moved = True
                        break  # Smoke moves and stops checking

                # 3. If smoke cannot move upwards → Move left or right
                if not moved:
                    if j > 0 and grid[i, j - 1] == EMPTY:  # Left EMPTY
                        new_grid[i, j] = EMPTY
                        new_grid[i, j - 1] = grid[i, j]
                        smoke_life[i, j - 1] = smoke_life[i, j]
                    elif j < cols - 1 and grid[i, j + 1] == EMPTY:  # Right EMPTY
                        new_grid[i, j] = EMPTY
                        new_grid[i, j + 1] = grid[i, j]
                        smoke_life[i, j + 1] = smoke_life[i, j]

            elif grid[i, j] == WATER:
                # 1. Move down if there is empty space below
                if i < rows - 1 and grid[i + 1, j] == EMPTY:
                    transfer = min(water_amount[i, j], 1.0 - water_amount[i + 1, j]) # Transfer water only if there is space
                    water_amount[i, j] -= transfer
                    water_amount[i + 1, j] += transfer
                    new_grid[i + 1, j] = WATER
                    if water_amount[i, j] == 0: # If there is no water left, set the cell to empty
                        new_grid[i, j] = EMPTY

                # 2. Spread left and right if the cells below are full
                if i < rows - 1 and (grid[i + 1, j] in [WALL, SAND, WOOD, WATER] ):
                    for dx in [-1, 1]:  # Left, Right
                        ni, nj = i, j + dx
                        if 0 <= ni < rows and 0 <= nj < cols:
                            # Check if the cell is empty or water and if there is enough water to transfer
                            if grid[ni, nj] in [EMPTY, WATER] and water_amount[i, j] > 0.01:
                                max_transfer = min(water_amount[i, j] * 0.5, 1.0 - water_amount[ni, nj])
                                water_amount[ni, nj] += max_transfer
                                water_amount[i, j] -= max_transfer
                                new_grid[ni, nj] = WATER
                                if water_amount[i, j] == 0: # If there is no water left, set the cell to empty
                                    new_grid[i, j] = EMPTY

                # 3. IF the ceels is bellow 0.01, set it to 0
                if water_amount[i, j] <= 0.01:
                    water_amount[i, j] = 0
                    new_grid[i, j] = EMPTY

                # 4. Move down if any neighboring cells below are not full (less than 100%)
                if i < rows - 1 and grid[i + 1, j] in [WATER]: # Check if the cell below is water
                    bottom_not_full = False
                    for dx in [-1, 0, 1]:  # left, center, right
                        ni, nj = i + 1, j + dx
                        if 0 <= ni < rows and 0 <= nj < cols:
                            if grid[ni, nj] == WATER and water_amount[ni, nj] < 1.0: # Check if the cell is full
                                bottom_not_full = True # downstairs cell is not full
                                break

                    # if there is empty space below, move water down
                    if bottom_not_full:
                        transfer = min(water_amount[i, j], 1.0 - water_amount[i + 1, j])
                        water_amount[i, j] -= transfer
                        water_amount[i + 1, j] += transfer
                        new_grid[i + 1, j] = WATER
                        if water_amount[i, j] == 0:
                            new_grid[i, j] = EMPTY

            elif grid[i, j] == ICE:
                # 1. Ice melts if there is fire nearby
                if (
                        (i > 0 and grid[i - 1, j] == FIRE) or
                        (i < rows - 1 and grid[i + 1, j] == FIRE) or
                        (j > 0 and grid[i, j - 1] == FIRE) or
                        (j < cols - 1 and grid[i, j + 1] == FIRE)
                ):
                    new_grid[i, j] = WATER
                    water_amount[i, j] = 0.25
                    continue

                # 2. Ice moves down if there is empty space below
                if i < rows - 1 and grid[i + 1, j] == EMPTY:
                    new_grid[i, j] = EMPTY
                    new_grid[i + 1, j] = ICE
                    continue

                # 3. Ice spreads if the cells below are full
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Levo, Desno, Gor, Dol
                    ni, nj = i + dx, j + dy
                    if 0 <= ni < rows and 0 <= nj < cols:
                        if grid[ni, nj] == WATER:
                            new_grid[ni, nj] = ICE

    return new_grid

# Function to draw the grid with textures
def draw_grid(grid):
    img = np.zeros((grid.shape[0] * 32, grid.shape[1] * 32, 3), dtype=np.uint8)
    # Loop through the grid and draw the textures
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            if grid[i, j] == WATER:
                water_level = water_amount[i, j]
                if water_level <= 0.25:
                    cell_texture = textures[WATER][0]
                elif water_level <= 0.5:
                    cell_texture = textures[WATER][1]
                elif water_level <= 0.75:
                    cell_texture = textures[WATER][2]
                else:
                    cell_texture = textures[WATER][3]
                img[i * 32:(i + 1) * 32, j * 32:(j + 1) * 32] = cell_texture

            else:
                img[i * 32:(i + 1) * 32, j * 32:(j + 1) * 32] = textures[grid[i, j]]

    return img

# Function for animating the simulation
def animate(frame_num, grid, img, steps, water_amount):
    new_grid = generate_next_gen(grid, steps, water_amount)
    img.set_data(draw_grid(new_grid))
    grid[:] = new_grid
    return img,

def create_test_environment(size):
    global smoke_life, water_amount
    grid = np.full((size, size), EMPTY)

    grid[5, 4:7] = SAND
    grid[6, 4:7] = SAND
    grid[7, 4:7] = SAND

    grid[8, 5] = WOOD
    grid[9, 5] = WOOD
    grid[8, 6] = WOOD
    grid[9, 6] = WOOD

    grid[10, 5] = FIRE
    grid[10, 6] = FIRE

    grid[12, 5] = SMOKE_DARK
    grid[12, 6] = SMOKE_LIGHT
    grid[13, 4] = SMOKE_LIGHT
    grid[13, 7] = SMOKE_DARK

    grid[3, :] = WALL
    grid[:, 3] = WALL
    grid[4:10, 8] = WALL
    grid[5, 2:6] = WALL
    grid[8, 0:3] = WALL
    grid[11, 6:9] = WALL

    smoke_life = np.zeros((size, size), dtype=int)
    water_amount = np.zeros((size, size), dtype=float)

    smoke_life[12, 5] = 20
    smoke_life[12, 6] = 15
    smoke_life[13, 4] = 10
    smoke_life[13, 7] = 18

    grid[6, 5] = WATER
    grid[7, 5] = WATER
    grid[8, 5] = WATER
    water_amount[6, 5] = 1.0
    water_amount[7, 5] = 0.5
    water_amount[8, 5] = 0.25

    return grid


