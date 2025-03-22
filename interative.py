import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib import animation
from PIL import Image
from avatar import generate_next_gen, draw_grid  # Uporaba funkcij iz avatar.py

# Constants for cell states
EMPTY = 0
WALL = 1
SAND = 2
WOOD = 3
FIRE = 4

# Element labels for buttons
element_labels = {
    EMPTY: "Prazno",
    WALL: "Stena",
    SAND: "Pesek",
    WOOD: "Les",
    FIRE: "Ogenj"
}

# Load textures for each element
textures = {
    EMPTY: np.array(Image.open("tiles/empty.png").convert("RGB")),
    WALL: np.array(Image.open("tiles/wall.png").convert("RGB")),
    SAND: np.array(Image.open("tiles/sand.png").convert("RGB")),
    WOOD: np.array(Image.open("tiles/wood.png").convert("RGB")),
    FIRE: np.array(Image.open("tiles/fire.png").convert("RGB")),
}

# Global variables
selected_element = EMPTY
grid = None  # Mreža bo ustvarjena v glavni funkciji

# Function to set the selected element
def set_element(element):
    global selected_element
    selected_element = element
    print(f"Izbran element: {element_labels[element]}")

def start_simulation(event):
    global grid  # Popravek: Uporabi globalno spremenljivko
    print("Začel bom simulacijo...")

    fig, ax = plt.subplots()

    def animate(frame_num):
        grid[:] = generate_next_gen(grid)  # Posodobi mrežo neposredno
        draw_grid(ax, len(grid))
        plt.draw()

    global ani  # Dodano: Da se animacija ohrani v spominu
    ani = animation.FuncAnimation(fig, animate, frames=50, interval=200)
    plt.show()


# Function to draw the grid with textures
def draw_grid(ax_grid, grid_size):
    ax_grid.clear()  # Očisti mrežo pred ponovnim risanjem
    img = np.zeros((grid_size * 32, grid_size * 32, 3), dtype=np.uint8)
    for i in range(grid_size):
        for j in range(grid_size):
            img[i * 32:(i + 1) * 32, j * 32:(j + 1) * 32] = textures[grid[i, j]]

    ax_grid.imshow(img)

    # Dodaj mrežne črte
    ax_grid.set_xticks(np.arange(0, grid_size * 32, 32))
    ax_grid.set_yticks(np.arange(0, grid_size * 32, 32))
    ax_grid.grid(True, color='black', linewidth=0.5)
    ax_grid.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

# Function to place elements on click
def on_click(event, ax_grid, grid_size):
    if event.inaxes == ax_grid:
        x, y = int(event.xdata // 32), int(event.ydata // 32)
        if 0 <= x < grid_size and 0 <= y < grid_size:
            grid[y, x] = selected_element
            draw_grid(ax_grid, grid_size)
            plt.draw()

# Main interactive simulation
def run_interactive_simulation(grid_size, steps):
    global grid
    grid = np.full((grid_size, grid_size), EMPTY)  # Mreža se ustvari tu

    grid[0, :] = WALL  # Zgornji rob
    grid[-1, :] = WALL  # Spodnji rob
    grid[:, 0] = WALL  # Levi rob
    grid[:, -1] = WALL  # Desni rob

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
    start_btn.on_clicked(start_simulation)

    # Draw initial grid
    draw_grid(ax_grid, grid_size)

    # Handle clicks for placing elements
    fig.canvas.mpl_connect('button_press_event', lambda event: on_click(event, ax_grid, grid_size))
    plt.show()

if __name__ == "__main__":
    size = 10
    steps = 100
    smoke_life = np.zeros((size, size), dtype=int)
    run_interactive_simulation(size, steps)
