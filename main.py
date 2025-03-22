import numpy as np
from matplotlib import pyplot as plt

# Funciton for converting rule from decimal to binary form (8-bit)
def get_rule_binary(rule_number):
    return np.array([int(x) for x in np.binary_repr(rule_number, width=8)])

# Function for generating next generation based on the rule
def generate_next_gen(current_gen, rule_binary):
    padded_gen = np.pad(current_gen, 1, mode='constant')  # Add padding to the current generation
    next_gen = np.zeros_like(current_gen)

    for i in range(len(current_gen)):
        neighborhood = padded_gen[i:i+3]  # Neighborhood of the current cell
        idx = 7 - int(''.join(map(str, neighborhood)), 2)  # Index of the rule
        next_gen[i] = rule_binary[idx]  # Apply the rule

    return next_gen

# Function for plotting the automaton
def plot_automaton(initial_gen, rule_number, steps=50):
    rule_binary = get_rule_binary(rule_number)
    generations = [initial_gen]

    for _ in range(steps - 1):
        generations.append(generate_next_gen(generations[-1], rule_binary))

    plt.imshow(generations, cmap='binary', interpolation='nearest')
    plt.title(f'1D Cellular Automaton - Rule {rule_number}')
    plt.xlabel('Cell Index')
    plt.ylabel('Generations')
    plt.show()


if __name__ == "__main__":
    rule_number = int(input("Vnesite pravilo (0-255): "))
    size = 100  # Size of the 1D automaton
    steps = 50  # Number of generations

    # Začetno stanje - ena aktivna celica v sredini
    initial_gen = np.zeros(size, dtype=int)
    initial_gen[size // 2] = 1

    plot_automaton(initial_gen, rule_number, steps)
