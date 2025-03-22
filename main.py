import numpy as np
from matplotlib import pyplot as plt
import matplotlib.animation as animation
from one import plot_automaton_1d
from two import create_initial_state_2d, animate

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
                                      lambda frame_num: animate(frame_num, initial_state, img, stable_counter, ani),
                                      frames=steps, interval=70, repeat=False)

        plt.title("2D Cellular Automaton - Rule B678/S2345678")
        plt.show()
