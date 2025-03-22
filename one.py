import numpy as np
from matplotlib import pyplot as plt

# Function for converting rule from decimal to binary form (8-bit)
def get_rule_binary(rule_number):
    return np.array([int(x) for x in np.binary_repr(rule_number, width=8)])

# Function for generating next generation based on the rule
def generate_next_gen_1d(current_gen, rule_binary):
    padded_gen = np.pad(current_gen, 1, mode='constant')  # Add padding to the current generation
    next_gen = np.zeros_like(current_gen)

    for i in range(len(current_gen)):
        neighborhood = padded_gen[i:i+3]  # Neighborhood of the current cell
        idx = 7 - int(''.join(map(str, neighborhood)), 2)  # Index of the rule
        next_gen[i] = rule_binary[idx]  # Apply the rule

    return next_gen

# Function for plotting the 1D automaton
def plot_automaton_1d(initial_gen, rule_number, steps=50):
    rule_binary = get_rule_binary(rule_number)
    generations = [initial_gen]

    for _ in range(steps - 1):
        generations.append(generate_next_gen_1d(generations[-1], rule_binary))

    plt.imshow(generations, cmap='binary', interpolation='nearest')
    plt.title(f'1D Cellular Automaton - Rule {rule_number}')
    plt.xlabel('Cell Index')
    plt.ylabel('Generations')
    plt.show()