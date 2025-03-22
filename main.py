import numpy as np
from matplotlib import pyplot as plt
import matplotlib.animation as animation
from one import plot_automaton_1d

# Function for creating initial 2D state
def create_initial_state_2d(size, fill_ratio=0.45):
    grid = np.random.choice([0, 1], size=(size, size), p=[1-fill_ratio, fill_ratio])
    grid[0:2, :] = grid[:, 0:2] = grid[-2:, :] = grid[:, -2:] = 0  # Fixed border
    return grid

# Function for generating next generation for 2D automaton
def generate_next_gen_2d(grid):
    new_grid = np.copy(grid)
    rows, cols = grid.shape

    for i in range(1, rows-1):  # Ignore the fixed border
        for j in range(1, cols-1):
            # Count live neighbors
            neighbors = np.sum(grid[i-1:i+2, j-1:j+2]) - grid[i, j]

            if grid[i, j] == 1:  # Alive cell
                if neighbors < 2 or neighbors > 8:
                    new_grid[i, j] = 0  # Cell dies
            else:  # Dead cell
                if neighbors in [6, 7, 8]:
                    new_grid[i, j] = 1  # Cell is born

    return new_grid

# Function for animating 2D automaton
def animate(frame_num, grid, img, stable_counter):
    new_grid = generate_next_gen_2d(grid)
    img.set_data(new_grid)

    # Check if grid stabilized for 15 steps
    if np.array_equal(grid, new_grid):
        stable_counter[0] += 1
    else:
        stable_counter[0] = 0  # Reset counter if grid changes

    if stable_counter[0] >= 15:  # Stop after 15 stable generations
        print("Stanje se je stabiliziralo po 15 stabilnih generacijah.")
        ani.event_source.stop()

    grid[:] = new_grid
    return img,

# Main Program
if __name__ == "__main__":
    automaton_type = input("Izberite vrsto avtomata (1/2): ").strip().lower()

    if automaton_type == "1":
        rule_number = int(input("Vnesite pravilo (0-255): "))
        size = 100
        steps = 50

        initial_gen = np.zeros(size, dtype=int)
        initial_gen[size // 2] = 1

        plot_automaton_1d(initial_gen, rule_number, steps)

    elif automaton_type == "2":
        size = 50
        steps = 150

        initial_state = create_initial_state_2d(size, fill_ratio=0.45)

        fig, ax = plt.subplots()
        img = ax.imshow(initial_state, cmap='gray')
        stable_counter = [0]
        ani = animation.FuncAnimation(fig, animate, fargs=(initial_state, img, stable_counter), frames=steps, interval=70, repeat=False)

        plt.title("2D Cellular Automaton - Rule B678/S2345678")
        plt.show()
