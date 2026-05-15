"""
Run ACO experiments and generate plots for the Results section.

Produces:
  - convergence_single.png       - best fitness over iterations for one run
  - convergence_aggregated.png   - mean best fitness across N seeds with std band
  - final_fitness_boxplot.png    - distribution of initial vs final fitness
  - n_ants_comparison.png        - convergence under different ant counts
  - pheromone_heatmap.png        - final pheromone distribution (slot x food)
  - summary_table.txt            - numeric summary across seeds
"""

import os
import sys
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

_project_root = Path(__file__).parent.parent.parent
os.chdir(_project_root / "genetic_algorithm")
sys.path.insert(0, str(_project_root))

from swarm_algorithm.aco import ACOFoodOptimizer


PLOTS_DIR = Path(__file__).parent / "plots"
PLOTS_DIR.mkdir(exist_ok=True)

SEEDS = [6, 26, 59, 60, 79, 93, 489, 608, 634, 684]
ITERATIONS = 50
N_ANTS = 20


def run_with_seed(seed: int, n_ants: int, iterations: int):
    np.random.seed(seed)
    aco = ACOFoodOptimizer(n_ants=n_ants, alpha=1, beta=3, rho=0.1)
    foods, amounts = aco.optimize(max_iterations=iterations)
    return aco, foods, amounts


def run_all_seeds(n_ants=N_ANTS, iterations=ITERATIONS):
    results = []
    for i, seed in enumerate(SEEDS, 1):
        start = time.time()
        aco, foods, amounts = run_with_seed(seed, n_ants, iterations)
        elapsed = time.time() - start
        print(f"  seed {seed:>4} ({i}/{len(SEEDS)})  final={aco.best_fitness:>8.1f}  time={elapsed:>5.1f}s")
        results.append({"seed": seed, "aco": aco, "foods": foods, "amounts": amounts})
    return results


def plot_convergence_single(results):
    history = results[0]["aco"].best_fitness_history
    iterations = np.arange(1, len(history) + 1)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(iterations, history, linewidth=2, color="#1f77b4")
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Best fitness (calorie deviation over week)")
    ax.set_title(f"ACO convergence - single run (seed={results[0]['seed']})")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "convergence_single.png", dpi=120)
    plt.close(fig)


def plot_convergence_aggregated(results):
    all_best = np.array([r["aco"].best_fitness_history for r in results])
    iterations = np.arange(1, all_best.shape[1] + 1)
    mean = all_best.mean(axis=0)
    std = all_best.std(axis=0)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(iterations, mean, linewidth=2, color="#2ca02c", label=f"Mean best fitness (n={len(results)})")
    ax.fill_between(iterations, mean - std, mean + std, alpha=0.25, color="#2ca02c", label="+/-1 std")
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Best fitness")
    ax.set_title("ACO convergence - aggregated across seeds")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "convergence_aggregated.png", dpi=120)
    plt.close(fig)


def plot_final_fitness_boxplot(results):
    final = [r["aco"].best_fitness for r in results]
    initial = [r["aco"].best_fitness_history[0] for r in results]

    fig, ax = plt.subplots(figsize=(7, 5))
    bp = ax.boxplot([initial, final], tick_labels=["Initial population", "Final solution"],
                    patch_artist=True, widths=0.5)
    for patch, color in zip(bp["boxes"], ["#ff7f0e", "#2ca02c"]):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    ax.set_ylabel("Best fitness")
    ax.set_title(f"ACO fitness distribution across {len(results)} seeds")
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "final_fitness_boxplot.png", dpi=120)
    plt.close(fig)


def plot_n_ants_comparison():
    ant_counts = [10, 20, 40]
    fig, ax = plt.subplots(figsize=(9, 5))

    for n_ants in ant_counts:
        all_best = []
        for seed in SEEDS[:3]:
            aco, _, _ = run_with_seed(seed, n_ants, ITERATIONS)
            all_best.append(aco.best_fitness_history)
        all_best = np.array(all_best)
        iterations = np.arange(1, all_best.shape[1] + 1)
        mean = all_best.mean(axis=0)
        ax.plot(iterations, mean, linewidth=2, label=f"Ants = {n_ants}")
        print(f"  ants={n_ants}  mean final={mean[-1]:.1f}")

    ax.set_xlabel("Iteration")
    ax.set_ylabel("Mean best fitness (3 seeds)")
    ax.set_title("Effect of ant count on ACO convergence")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "n_ants_comparison.png", dpi=120)
    plt.close(fig)


def plot_pheromone_heatmap(results):
    aco = results[0]["aco"]
    pheromone = aco.pheromone

    # Show only the top-N foods by total pheromone for readability
    top_n = 50
    food_totals = pheromone.sum(axis=0)
    top_foods = np.argsort(food_totals)[-top_n:][::-1]
    pheromone_top = pheromone[:, top_foods]

    fig, ax = plt.subplots(figsize=(12, 7))
    im = ax.imshow(pheromone_top, aspect="auto", cmap="Oranges", interpolation="nearest")
    ax.set_xlabel(f"Food index (top {top_n} by total pheromone)")
    ax.set_ylabel("Meal slot (0..76)")
    ax.set_title(f"Final pheromone heatmap (seed={results[0]['seed']})")
    fig.colorbar(im, ax=ax, label="Pheromone strength")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "pheromone_heatmap.png", dpi=120)
    plt.close(fig)


def write_summary(results):
    final = np.array([r["aco"].best_fitness for r in results])
    initial = np.array([r["aco"].best_fitness_history[0] for r in results])
    improvement = initial - final

    lines = [
        "ACO Experiment Summary",
        "=" * 60,
        f"Seeds:          {len(results)}",
        f"Ants:           {N_ANTS}",
        f"Iterations:     {ITERATIONS}",
        "",
        f"Initial best fitness  - mean: {initial.mean():>9.2f}  std: {initial.std():>7.2f}",
        f"Final best fitness    - mean: {final.mean():>9.2f}  std: {final.std():>7.2f}",
        f"Improvement (kcal)    - mean: {improvement.mean():>9.2f}  std: {improvement.std():>7.2f}",
        f"Improvement ratio     - mean: {(improvement / initial).mean() * 100:>8.1f}%",
        "",
        "Per-seed results:",
        f"  {'seed':>4} | {'initial':>10} | {'final':>10} | {'improvement':>11}",
    ]
    for r in results:
        seed = r["seed"]
        init_fit = r["aco"].best_fitness_history[0]
        final_fit = r["aco"].best_fitness
        lines.append(f"  {seed:>4} | {init_fit:>10.2f} | {final_fit:>10.2f} | {init_fit - final_fit:>11.2f}")

    summary = "\n".join(lines)
    (PLOTS_DIR / "summary_table.txt").write_text(summary)
    print("\n" + summary)


def main():
    print(f"Running ACO across {len(SEEDS)} seeds  (ants={N_ANTS}, iters={ITERATIONS})")
    results = run_all_seeds()

    print("\nGenerating plots...")
    plot_convergence_single(results)
    plot_convergence_aggregated(results)
    plot_final_fitness_boxplot(results)
    plot_pheromone_heatmap(results)

    print("\nRunning ant-count comparison...")
    plot_n_ants_comparison()

    write_summary(results)

    print(f"\nDone. Plots saved to: {PLOTS_DIR}")


if __name__ == "__main__":
    main()
