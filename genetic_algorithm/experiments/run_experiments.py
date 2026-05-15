"""
Run genetic algorithm experiments and generate plots for the Results section.

Produces:
  - convergence_single.png       — best vs avg fitness for one representative run
  - convergence_aggregated.png   — mean best fitness across N seeds with std band
  - diversity.png                — unique foods in population over generations
  - final_fitness_boxplot.png    — distribution of final best fitness across seeds
  - population_size_comparison.png — convergence under different population sizes
  - summary_table.txt            — numeric summary across seeds
"""

import os
import random
import sys
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

_project_root = Path(__file__).parent.parent.parent
os.chdir(_project_root / "genetic_algorithm")
sys.path.insert(0, str(_project_root))

from genetic_algorithm.genetic_algorithm import GeneticAlgorithm


PLOTS_DIR = Path(__file__).parent / "plots"
PLOTS_DIR.mkdir(exist_ok=True)

SEEDS = [6, 26, 59, 60, 79, 93, 489, 608, 634, 684]
ITERATIONS = 150
POPULATION_SIZE = 60


def run_with_seed(seed: int, population_size: int, iterations: int):
    random.seed(seed)
    ga = GeneticAlgorithm()
    best, history = ga.run(population_size=population_size, iterations=iterations)
    return best, history


def run_all_seeds(population_size=POPULATION_SIZE, iterations=ITERATIONS):
    results = []
    for i, seed in enumerate(SEEDS, 1):
        start = time.time()
        best, history = run_with_seed(seed, population_size, iterations)
        elapsed = time.time() - start
        print(f"  seed {seed:>6} ({i}/{len(SEEDS)})  final={best.fitness:>8.1f}  time={elapsed:>5.1f}s")
        results.append({"seed": seed, "best": best, "history": history})
    return results


def plot_convergence_single(results):
    history = results[0]["history"]
    generations = np.arange(1, len(history) + 1)
    best_fitness = [h["best_fitness"] for h in history]
    avg_fitness = [h["avg_fitness"] for h in history]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(generations, best_fitness, label="Best fitness", linewidth=2, color="#1f77b4")
    ax.plot(generations, avg_fitness, label="Average fitness", linewidth=1.5, color="#ff7f0e", alpha=0.8)
    ax.set_xlabel("Generation")
    ax.set_ylabel("Fitness (sum of |daily calorie deviation|)")
    ax.set_title(f"Convergence — single run (seed={results[0]['seed']})")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "convergence_single.png", dpi=120)
    plt.close(fig)


def plot_convergence_aggregated(results):
    all_best = np.array([[h["best_fitness"] for h in r["history"]] for r in results])
    generations = np.arange(1, all_best.shape[1] + 1)
    mean = all_best.mean(axis=0)
    std = all_best.std(axis=0)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(generations, mean, label=f"Mean best fitness (n={len(results)})", linewidth=2, color="#2ca02c")
    ax.fill_between(generations, mean - std, mean + std, alpha=0.25, color="#2ca02c", label="±1 std")
    ax.set_xlabel("Generation")
    ax.set_ylabel("Best fitness")
    ax.set_title("Convergence — aggregated across seeds")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "convergence_aggregated.png", dpi=120)
    plt.close(fig)


def plot_diversity(results):
    all_diversity = np.array([[h["unique_foods"] for h in r["history"]] for r in results])
    generations = np.arange(1, all_diversity.shape[1] + 1)
    mean = all_diversity.mean(axis=0)
    std = all_diversity.std(axis=0)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(generations, mean, linewidth=2, color="#d62728", label=f"Mean unique foods (n={len(results)})")
    ax.fill_between(generations, mean - std, mean + std, alpha=0.25, color="#d62728", label="±1 std")
    ax.set_xlabel("Generation")
    ax.set_ylabel("Unique food items in population")
    ax.set_title("Population diversity over generations")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "diversity.png", dpi=120)
    plt.close(fig)


def plot_final_fitness_boxplot(results):
    final = [r["best"].fitness for r in results]
    initial = [r["history"][0]["best_fitness"] for r in results]

    fig, ax = plt.subplots(figsize=(7, 5))
    bp = ax.boxplot([initial, final], tick_labels=["Initial population", "Final solution"],
                    patch_artist=True, widths=0.5)
    for patch, color in zip(bp["boxes"], ["#ff7f0e", "#2ca02c"]):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    ax.set_ylabel("Best fitness")
    ax.set_title(f"Fitness distribution across {len(results)} seeds")
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "final_fitness_boxplot.png", dpi=120)
    plt.close(fig)


def plot_population_size_comparison():
    sizes = [30, 60, 100]
    iterations = ITERATIONS
    fig, ax = plt.subplots(figsize=(9, 5))

    for size in sizes:
        all_best = []
        for seed in SEEDS[:3]:
            _, history = run_with_seed(seed, size, iterations)
            all_best.append([h["best_fitness"] for h in history])
        all_best = np.array(all_best)
        generations = np.arange(1, all_best.shape[1] + 1)
        mean = all_best.mean(axis=0)
        ax.plot(generations, mean, linewidth=2, label=f"Population = {size}")
        print(f"  pop={size}  mean final={mean[-1]:.1f}")

    ax.set_xlabel("Generation")
    ax.set_ylabel("Mean best fitness (3 seeds)")
    ax.set_title("Effect of population size on convergence")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "population_size_comparison.png", dpi=120)
    plt.close(fig)


def write_summary(results):
    final = np.array([r["best"].fitness for r in results])
    initial = np.array([r["history"][0]["best_fitness"] for r in results])
    improvement = initial - final

    lines = [
        "Experiment Summary",
        "=" * 60,
        f"Seeds:          {len(results)}",
        f"Population:     {POPULATION_SIZE}",
        f"Iterations:     {ITERATIONS}",
        "",
        f"Initial best fitness  - mean: {initial.mean():>9.2f}  std: {initial.std():>7.2f}",
        f"Final best fitness    - mean: {final.mean():>9.2f}  std: {final.std():>7.2f}",
        f"Improvement (kcal)    - mean: {improvement.mean():>9.2f}  std: {improvement.std():>7.2f}",
        f"Improvement ratio     - mean: {(improvement / initial).mean() * 100:>8.1f}%",
        "",
        "Per-seed results:",
        f"  {'seed':>6} | {'initial':>10} | {'final':>10} | {'improvement':>11}",
    ]
    for r in results:
        seed = r["seed"]
        init_fit = r["history"][0]["best_fitness"]
        final_fit = r["best"].fitness
        lines.append(f"  {seed:>6} | {init_fit:>10.2f} | {final_fit:>10.2f} | {init_fit - final_fit:>11.2f}")

    summary = "\n".join(lines)
    (PLOTS_DIR / "summary_table.txt").write_text(summary)
    print("\n" + summary)


def main():
    print(f"Running GA across {len(SEEDS)} seeds  (pop={POPULATION_SIZE}, iters={ITERATIONS})")
    results = run_all_seeds()

    print("\nGenerating plots...")
    plot_convergence_single(results)
    plot_convergence_aggregated(results)
    plot_diversity(results)
    plot_final_fitness_boxplot(results)

    print("\nRunning population-size comparison...")
    plot_population_size_comparison()

    write_summary(results)

    print(f"\nDone. Plots saved to: {PLOTS_DIR}")


if __name__ == "__main__":
    main()