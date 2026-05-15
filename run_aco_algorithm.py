import os
import sys

_project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(_project_root, "genetic_algorithm"))
sys.path.insert(0, _project_root)

from data_models.database import FOOD_DATABASE
from data_models.individual import Individual
from swarm_algorithm.aco import ACOFoodOptimizer
from wrapper_helper_functions import translate_sol


def print_history(history: list[float]) -> None:
    print("=" * 60)
    print("ITERATION HISTORY")
    print("=" * 60)
    print(f"{'Iter':>5} | {'Best Fitness':>14}")
    print("-" * 60)

    step = max(1, len(history) // 20)
    for i, fitness in enumerate(history):
        if i % step == 0 or i == len(history) - 1:
            print(f"{i + 1:>5} | {fitness:>14.2f}")

    print("-" * 60)
    if history:
        improvement = history[0] - history[-1]
        print(f"Total improvement: {improvement:.2f} kcal/week closer to target")
    print()


def print_meal_plan(foods, amounts) -> None:
    individual = Individual(foods, amounts)

    print("=" * 60)
    print("BEST MEAL PLAN")
    print(f"Total fitness (calorie deviation over week): {individual.fitness:.2f} kcal")
    print("=" * 60)

    menu, daily_data = translate_sol(individual.foods, FOOD_DATABASE, individual.amounts)

    for day, meals in menu.items():
        print(f"\n{day.upper()}")
        print(f"  Daily calories: {daily_data[day]['calories']:.0f} kcal")
        for meal_name, (food_items, calories) in meals.items():
            print(f"  {meal_name} ({calories:.0f} kcal):")
            for food in food_items:
                print(f"    {food}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--ants", type=int, default=30)
    parser.add_argument("--iterations", type=int, default=100)
    args = parser.parse_args()

    aco = ACOFoodOptimizer(n_ants=args.ants, alpha=1, beta=3, rho=0.1)

    print(f"Ants: {args.ants} | Iterations: {args.iterations}\n")

    best_foods, best_amounts = aco.optimize(max_iterations=args.iterations)

    print_history(aco.best_fitness_history)
    print_meal_plan(best_foods, best_amounts)
