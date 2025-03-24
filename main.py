import numpy as np
from matplotlib import pyplot as plt
import matplotlib.animation as animation
from one import plot_automaton_1d
from two import create_initial_state_2d, animate2
from avatar import create_initial_state, draw_grid, animate, create_test_environment
from interative import run_interactive_simulation

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
        ani = animation.FuncAnimation(fig,
                                      lambda frame_num: animate2(frame_num, initial_state, img, stable_counter, ani),
                                      frames=steps, interval=70, repeat=False)

        plt.title("2D Cellular Automaton - Rule B678/S2345678")
        plt.show()

    elif automaton_type == "3":
        size = 20
        steps = 100

        initial_state = create_initial_state(size)
        water_amount = np.zeros((size, size), dtype=float)

        fig, ax = plt.subplots()
        img = ax.imshow(draw_grid(initial_state))
        ani = animation.FuncAnimation(fig, animate, fargs=(initial_state, img, steps, water_amount), frames=steps, interval=70, repeat=False)

        plt.title("2D Cellular Automaton - Sand, Wood, Fire, and Smoke")
        plt.show()

    elif automaton_type == "4":
        size = 20
        steps = 100

        initial_state = create_test_environment(size)
        smoke_life = np.zeros((size, size), dtype=int)
        water_amount = np.zeros((size, size), dtype=float)

        fig, ax = plt.subplots()
        img = ax.imshow(draw_grid(initial_state))
        ani = animation.FuncAnimation(fig, animate, fargs=(initial_state, img, steps, water_amount), frames=steps, interval=70, repeat=False)

        plt.title("Testno okolje - Pesek, Les, Ogenj in Dim")
        plt.show()

    elif automaton_type == "5":
        size = 20
        steps = 100
        run_interactive_simulation(size, steps)

