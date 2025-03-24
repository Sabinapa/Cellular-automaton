import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib import animation
from PIL import Image
from avatar import generate_next_gen, draw_grid

EMPTY = 0
WALL = 1
SAND = 2
WOOD = 3
FIRE = 4
SMOKE_DARK = 5
SMOKE_LIGHT = 6
WATER = 7

# Element labels for buttons
element_labels = {
    EMPTY: "Prazno",
    WALL: "Stena",
    SAND: "Pesek",
    WOOD: "Les",
    FIRE: "Ogenj",
    WATER: "Voda"
}

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
    ]
}

# Global variables
selected_element = EMPTY
grid = None  # Grid is created in run_interactive_simulation
water_amount = None

# Function to set the selected element
def set_element(element):
    global selected_element
    selected_element = element
    print(f"Izbran element: {element_labels[element]}")

def start_simulation(steps):
    global grid, ani
    print("Začel bom simulacijo...")

    fig, ax = plt.subplots()

    def animate(frame_num):
        global grid, smoke_life, water_amount
        grid[:] = generate_next_gen(grid, steps, water_amount)  # Update grid
        draw_grid(ax, len(grid))
        plt.draw()

    ani = animation.FuncAnimation(fig, animate, frames=steps, interval=300)
    plt.show()


# Function to draw the grid with textures
def draw_grid(ax_grid, grid_size):
    global water_amount
    if water_amount is None:
        water_amount = np.zeros((grid_size, grid_size), dtype=float)

    ax_grid.clear()
    img = np.zeros((grid_size * 32, grid_size * 32, 3), dtype=np.uint8)
    for i in range(grid_size):
        for j in range(grid_size):
            if grid[i, j] == WATER:
                water_level = water_amount[i, j]
                print(f"Risanje celice ({i}, {j}) z nivojem {water_level:.2f} vode.")  # Dodan izpis
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

    ax_grid.imshow(img)

    # Set grid lines
    ax_grid.set_xticks(np.arange(0, grid_size * 32, 32))
    ax_grid.set_yticks(np.arange(0, grid_size * 32, 32))
    ax_grid.grid(True, color='black', linewidth=0.5)
    ax_grid.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

# Function to place elements on click
def on_click(event, ax_grid, grid_size):
    if event.inaxes == ax_grid:
        x, y = int(event.xdata // 32), int(event.ydata // 32)
        if 0 <= x < grid_size and 0 <= y < grid_size:
            if selected_element == WATER:
                if grid[y, x] == WATER:
                    water_amount[y, x] = min(water_amount[y, x] + 0.25, 1.5)  # Dvigni nivo vode do 150%
                else:
                    grid[y, x] = WATER
                    water_amount[y, x] = 0.25  # Prvotni klik postavi začetni nivo vode
            else:
                grid[y, x] = selected_element

            draw_grid(ax_grid, grid_size)
            plt.draw()


def run_interactive_simulation(grid_size, steps):
    global grid, smoke_life, water_amount
    grid = np.full((grid_size, grid_size), EMPTY)  # Create empty grid

    grid[0, :] = WALL  # Zgornji rob
    grid[-1, :] = WALL  # Spodnji rob
    grid[:, 0] = WALL  # Levi rob
    grid[:, -1] = WALL  # Desni rob

    smoke_life = np.zeros((grid_size, grid_size), dtype=int)
    water_amount = np.zeros((grid_size, grid_size), dtype=float)

    # Setup figure
    fig, (ax_buttons, ax_grid) = plt.subplots(1, 2, figsize=(10, 6))
    ax_buttons.axis('off')

    # Create element selection buttons
    buttons = []
    for idx, (element, label) in enumerate(element_labels.items()):
        ax_button = plt.axes([0.02, 0.8 - 0.1 * idx, 0.13, 0.08])
        btn = Button(ax_button, label)
        btn.on_clicked(lambda _, el=element: set_element(el))
        buttons.append(btn)

    # Add "Start Simulation" button
    start_btn = Button(plt.axes([0.02, 0.1, 0.13, 0.08]), 'Začni simulacijo')
    start_btn.on_clicked(lambda _: start_simulation(steps))

    # Draw initial grid
    draw_grid(ax_grid, grid_size)

    # Handle clicks for placing elements
    fig.canvas.mpl_connect('button_press_event', lambda event: on_click(event, ax_grid, grid_size))
    plt.show()

if __name__ == "__main__":
    size = 20
    steps = 50
    smoke_life = np.zeros((size, size), dtype=int)
    run_interactive_simulation(size, steps)
