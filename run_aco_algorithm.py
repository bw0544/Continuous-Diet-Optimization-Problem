from wrapper_helper_functions import translate_sol
from aco_algorithm.aco_algorithm import ACOAlgorithm
from data_models.database import FOOD_DATABASE
import os
import sys

_project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(_project_root, "aco_algorithm"))
sys.path.insert(0, _project_root)


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


if __name__ == "__main__":
    ga = ACOAlgorithm()
    print("Running ACO Algorithm...")
    print(f"Population: 100 | Iterations: 500\n")

    best, history = ga.run(population_size=100, iterations=500)

    print_history(history)
    print_meal_plan(best)
