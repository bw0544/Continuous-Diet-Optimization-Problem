# ACO Meal Planner + Visualization

from typing import List
from itertools import accumulate
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import sys
import os
from data_models.database import FOOD_DATABASE
from aco_algorithm.aco_algorithm import ACOAlgorithm
from wrapper_helper_functions import translate_sol


_project_root = os.path.dirname(os.path.abspath(__file__))

sns.set_style('darkgrid')


def print_history(history: list[dict]) -> None:
    print("=" * 60)
    print("GENERATION HISTORY")
    print("=" * 60)
    print(f"{'Gen':>5} | {'Best Fitness':>14} | {'Avg Fitness':>13} | {'Unique Foods':>12}")
    print("-" * 60)

    step = max(1, len(history) // 20)
    for i, entry in enumerate(history):
        if i % step == 0 or i == len(history) - 1:
            print(
                f"{i + 1:>5} | {entry['best_fitness']:>14.2f} | {entry['avg_fitness']:>13.2f} | {entry['unique_foods']:>12}")

    print("-" * 60)
    improvement = history[0]["best_fitness"] - history[-1]["best_fitness"]
    print(f"Total improvement: {improvement:.2f} kcal/week closer to target")
    print()


def print_meal_plan(best_individual) -> None:
    print("=" * 60)
    print("BEST MEAL PLAN")
    print(
        f"Total fitness (calorie deviation over week): {best_individual.fitness:.2f} kcal")
    print("=" * 60)

    menu, daily_data = translate_sol(
        best_individual.foods, FOOD_DATABASE, best_individual.amounts)

    for day, meals in menu.items():
        print(f"\n{day.upper()}")
        print(f"  Daily calories: {daily_data[day]['calories']:.0f} kcal")
        for meal_name, (foods, calories) in meals.items():
            print(f"  {meal_name} ({calories:.0f} kcal):")
            for food in foods:
                print(f"    {food}")


# -----------------------------
# Visualization Functions
# -----------------------------

def plot_pheromone_heatmap(ga):
    """Plot pheromone evolution heatmap"""

    if not hasattr(ga, 'pheromone_history'):
        print("No pheromone history found.")
        return

    pheromones = np.array(ga.pheromone_history)

    plt.figure(figsize=(10, 6))
    sns.heatmap(
        pheromones,
        cmap='Oranges',
        xticklabels=100,
        yticklabels=100
    )

    plt.title('Pheromone Heatmap')
    plt.xlabel('Food Index / Decision Variable')
    plt.ylabel('Iterations')
    plt.tight_layout()
    plt.show()


def plot_fitness_evolution(ga):
    """Plot best/median/min/max fitness over iterations"""

    if not hasattr(ga, 'trails_history'):
        print("No trails history found.")
        return

    fitness = np.array([
        [ant[1] for ant in trails]
        for trails in ga.trails_history
    ])

    if hasattr(ga, 'best_fitness_history'):
        best_fitness = np.array(ga.best_fitness_history)
    else:
        best_fitness = np.min(fitness, axis=1)

    fig, axs = plt.subplots(figsize=(7, 5))

    axs.set_title('Fitness Evolution')
    axs.set_xlabel('Iterations')
    axs.set_ylabel('Fitness')

    axs.plot(best_fitness, label='Best Fitness', linewidth=2)

    median = np.median(fitness, axis=1)
    min_values = np.min(fitness, axis=1)
    max_values = np.max(fitness, axis=1)

    axs.plot(median, label='Median Fitness')

    axs.fill_between(
        np.arange(len(median)),
        min_values,
        max_values,
        alpha=0.3,
        color='orange',
        label='Min-Max Range'
    )

    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_diversity_evolution(ga):
    """Plot population diversity over iterations"""

    if not hasattr(ga, 'trails_history'):
        print("No trails history found.")
        return

    population = np.array([
        [np.array(ant[0]) for ant in trails]
        for trails in ga.trails_history
    ])

    diversity = np.sum(np.std(population, axis=1), axis=1)

    fig, axs = plt.subplots(figsize=(7, 5))

    axs.set_title('Diversity Evolution')
    axs.set_xlabel('Iterations')
    axs.set_ylabel('Diversity')

    axs.plot(diversity, color='orange', linewidth=2)

    plt.tight_layout()
    plt.show()


def stringify_individual(individual: List[int]) -> str:
    return ''.join([str(int(i)) for i in individual])


def plot_unique_solutions(ga):
    """Plot cumulative number of unique solutions found"""

    if not hasattr(ga, 'trails_history'):
        print("No trails history found.")
        return

    population = np.array([
        [np.array(ant[0]) for ant in trails]
        for trails in ga.trails_history
    ])

    a = np.apply_along_axis(stringify_individual, 2, population)

    a = list(accumulate(
        a,
        lambda x, y: x.union(set(y)),
        initial=set()
    ))

    fig, axs = plt.subplots(figsize=(7, 5))

    axs.plot([len(x) for x in a], color='orange', linewidth=2)

    axs.set_title('Unique Solutions Evolution')
    axs.set_xlabel('Iterations')
    axs.set_ylabel('Unique Solutions')

    plt.tight_layout()
    plt.show()


def plot_all(ga):
    """Run all visualization plots"""

    print("Generating visualizations...")

    try:
        plot_pheromone_heatmap(ga)
    except Exception as e:
        print(f"Error plotting pheromone heatmap: {e}")

    try:
        plot_fitness_evolution(ga)
    except Exception as e:
        print(f"Error plotting fitness evolution: {e}")

    try:
        plot_diversity_evolution(ga)
    except Exception as e:
        print(f"Error plotting diversity evolution: {e}")

    try:
        plot_unique_solutions(ga)
    except Exception as e:
        print(f"Error plotting unique solutions: {e}")


# -----------------------------
# Main
# -----------------------------

if __name__ == "__main__":
    ga = ACOAlgorithm()

    print("Running ACO Algorithm...")
    print(f"Population: 100 | Iterations: 500\n")

    best, history = ga.run(
        population_size=100,
        iterations=500
    )

    print_history(history)
    print_meal_plan(best)

    # Generate visualizations
    plot_all(ga)
