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
    #grid=np.random.choice([EMPTY, WALL, SAND, WOOD, FIRE, WATER, ICE],
                            size=(size, size),
    #                        p=[0.2, 0.2, 0.1, 0.1, 0.1, 0.2, 0.1])
                             p = [0.2, 0.2, 0.2, 0.2, 0.2])

    global smoke_life  # Spremenljivko označi kot globalno
    smoke_life = np.zeros((size, size), dtype=int)
    water_amount = np.zeros((size, size), dtype=float)

    # Dodeli začetno življenjsko dobo dima
    smoke_life[12, 5] = 20

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

    new_grid = np.copy(grid)
    rows, cols = grid.shape

    for i in range(rows-2, 0, -1):
        for j in range(1, cols-1):
            if grid[i, j] == WALL:
                continue  # Wall stays in the same place

            if grid[i, j] == SAND:
                # 1️⃣ Če je pod peskom prazen prostor, pade naravnost dol
                if i < grid.shape[0] - 1 and grid[i + 1, j] == EMPTY:
                    new_grid[i, j] = EMPTY
                    new_grid[i + 1, j] = SAND

                # 2️⃣ Če je pod peskom voda → Pesek izpodrine vodo
                elif i < grid.shape[0] - 1 and grid[i + 1, j] == WATER:
                    moved = False

                    # Poskusi izpodriniti vodo levo/desno
                    directions = [(0, -1), (0, 1)]
                    np.random.shuffle(directions)

                    for di, dj in directions:
                        ni, nj = i + 1, j + dj

                        if 0 <= nj < grid.shape[1] and grid[ni, nj] == EMPTY:
                            # Premakni vodo levo/desno
                            new_grid[ni, nj] = WATER
                            new_grid[i + 1, j] = SAND
                            moved = True
                            break  # Ko pesek izrine vodo, ne preverja več

                    # 3️⃣ Če ni možnosti za premik levo/desno → Zamenja mesto z vodo
                    if not moved:
                        new_grid[i, j] = WATER
                        new_grid[i + 1, j] = SAND

                # 4️⃣ Če se ne more premakniti navzdol → Preveri diagonalno premikanje
                else:
                    directions = [(1, -1), (1, 1)]
                    np.random.shuffle(directions)

                    for di, dj in directions:
                        ni, nj = i + di, j + dj
                        if 0 <= ni < grid.shape[0] and 0 <= nj < grid.shape[1]:
                            if grid[ni, nj] == EMPTY:
                                new_grid[i, j] = EMPTY
                                new_grid[ni, nj] = SAND
                                break  # Premik izveden

                    # 5️⃣ Če ni nobene možnosti za premik, ostane na mestu
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

                if i > 0 and grid[i - 1, j] == WATER:
                    new_grid[i - 1, j] = WOOD
                    new_grid[i, j] = WATER
                    water_amount[i, j] = min(water_amount[i, j] + 0.5, 1.0)

                    # 3️⃣ Preveri, če je les ujet med celicami z 100% vode (za dodatno preverbo)
                left_full = j > 0 and grid[i, j - 1] == WATER and water_amount[i, j - 1] >= 1.0
                right_full = j < cols - 1 and grid[i, j + 1] == WATER and water_amount[i, j + 1] >= 1.0

                if left_full or right_full:
                    if i > 0 and grid[i - 1, j] == EMPTY:
                        new_grid[i - 1, j] = WOOD
                        new_grid[i, j] = WATER
                        water_amount[i, j] = min(water_amount[i, j] + 0.5, 1.0)
                        continue

            elif grid[i, j] == FIRE:
                # 1. Fire moves downwards
                if i < rows - 1:  # Preverimo, da ni na dnu mreže
                    if grid[i + 1, j] == EMPTY:
                        new_grid[i, j] = EMPTY
                        new_grid[i + 1, j] = FIRE

                    # 2. Če je pod ognjem gorljiv element (les) → Temen dim
                    elif grid[i + 1, j] == WOOD:
                        new_grid[i + 1, j] = FIRE  # Požge les
                        new_grid[i, j] = SMOKE_DARK  # Ogenj se spremeni v temen dim
                        smoke_life[i, j] = steps #Life span of smoke

                    # 3. Če se ne more premakniti navzdol → Svetel dim
                    else:
                        new_grid[i, j] = SMOKE_LIGHT
                        smoke_life[i, j] = steps

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

            elif grid[i, j] == WATER:
                # 🔽 1. Premik navzdol, če je spodaj prazen prostor
                if i < rows - 1 and grid[i + 1, j] == EMPTY:
                    transfer = min(water_amount[i, j], 1.0 - water_amount[i + 1, j])
                    water_amount[i, j] -= transfer
                    water_amount[i + 1, j] += transfer
                    new_grid[i + 1, j] = WATER
                    if water_amount[i, j] == 0:
                        new_grid[i, j] = EMPTY

                # 🔄 2. Razlivanje levo in desno, če so spodnje celice polne
                if i < rows - 1 and grid[i + 1, j] in [WALL, SAND, WOOD, WATER]:
                    for dx in [-1, 1]:  # Levo in desno
                        ni, nj = i, j + dx
                        if 0 <= ni < rows and 0 <= nj < cols:
                            if grid[ni, nj] in [EMPTY, WATER] and water_amount[i, j] > 0.01:
                                max_transfer = min(water_amount[i, j] * 0.5, 1.0 - water_amount[ni, nj])
                                water_amount[ni, nj] += max_transfer
                                water_amount[i, j] -= max_transfer
                                new_grid[ni, nj] = WATER
                                if water_amount[i, j] == 0:
                                    new_grid[i, j] = EMPTY

                # 🔼 3. Premik navzgor le, če so spodnje in stranske celice napolnjene 100%
                if i < rows - 1 and grid[i + 1, j] in [EMPTY, WATER]:
                    # Preveri, če spodnje celice v oviri še niso 100% polne
                    bottom_not_full = False
                    for dx in [-1, 0, 1]:  # Levo, sredina, desno
                        ni, nj = i + 1, j + dx
                        if 0 <= ni < rows and 0 <= nj < cols:
                            if grid[ni, nj] == WATER and water_amount[ni, nj] < 1.0:
                                bottom_not_full = True
                                break

                    # Če spodnje celice niso polne, premakni vodo navzdol
                    if bottom_not_full:
                        transfer = min(water_amount[i, j], 1.0 - water_amount[i + 1, j])
                        water_amount[i, j] -= transfer
                        water_amount[i + 1, j] += transfer
                        new_grid[i + 1, j] = WATER
                        if water_amount[i, j] == 0:
                            new_grid[i, j] = EMPTY

            elif grid[i, j] == ICE:
                # 🔥 1. Led se stopi v stik z ognjem in postane voda (0.25)
                if (
                        (i > 0 and grid[i - 1, j] == FIRE) or
                        (i < rows - 1 and grid[i + 1, j] == FIRE) or
                        (j > 0 and grid[i, j - 1] == FIRE) or
                        (j < cols - 1 and grid[i, j + 1] == FIRE)
                ):
                    new_grid[i, j] = WATER
                    water_amount[i, j] = 0.25
                    continue

                # ⬇️ 2. Led pade dol, dokler ne naleti na oviro
                if i < rows - 1 and grid[i + 1, j] == EMPTY:
                    new_grid[i, j] = EMPTY
                    new_grid[i + 1, j] = ICE
                    continue

                # ❄️ 3. Led zamrzne sosednje celice z vodo
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Levo, Desno, Gor, Dol
                    ni, nj = i + dx, j + dy
                    if 0 <= ni < rows and 0 <= nj < cols:
                        if grid[ni, nj] == WATER:
                            new_grid[ni, nj] = ICE

    return new_grid

# Function to draw the grid with textures
def draw_grid(grid):
    img = np.zeros((grid.shape[0] * 32, grid.shape[1] * 32, 3), dtype=np.uint8)
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            if grid[i, j] == WATER:
                water_level = water_amount[i, j]
                if water_level <= 0.25:
                    cell_texture = textures[WATER][0]  # 1/4 polna celica
                elif water_level <= 0.5:
                    cell_texture = textures[WATER][1]  # 1/2 polna celica
                elif water_level <= 0.75:
                    cell_texture = textures[WATER][2]  # 3/4 polna celica
                else:
                    cell_texture = textures[WATER][3]  # Polna celica

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
    water_amount = np.zeros((size, size), dtype=float)

    # Nastavi življenjsko dobo dima
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


