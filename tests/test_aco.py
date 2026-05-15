import numpy as np
import pytest

from data_models.database import FOOD_DATABASE
from data_models.individual import Individual
from data_models.subject import TEST_SUBJECT_JOHN
from swarm_algorithm.aco import ACOFoodOptimizer


# ── helpers ──────────────────────────────────────────────────────────────────

def make_aco(n_ants=5, **kwargs):
    return ACOFoodOptimizer(n_ants=n_ants, **kwargs)


# ── ACOFoodOptimizer initialization ──────────────────────────────────────────

class TestACOInit:

    def test_default_uses_food_database(self):
        aco = make_aco()
        assert len(aco.foods) == len(FOOD_DATABASE)

    def test_default_uses_test_subject_calories(self):
        aco = make_aco()
        assert aco.target_calories == TEST_SUBJECT_JOHN.daily_calories

    def test_custom_foods_accepted(self):
        custom_foods = FOOD_DATABASE[:50]
        aco = make_aco(foods=custom_foods)
        assert len(aco.foods) == 50

    def test_custom_target_accepted(self):
        aco = make_aco(target_calories=1800)
        assert aco.target_calories == 1800

    def test_total_slots_is_77(self):
        aco = make_aco()
        assert aco.total_slots == 77

    def test_days_is_7(self):
        aco = make_aco()
        assert aco.days == 7

    def test_foods_per_day_is_11(self):
        aco = make_aco()
        assert aco.foods_per_day == 11

    def test_calories_array_matches_foods(self):
        aco = make_aco()
        assert len(aco.calories) == len(aco.foods)

    def test_valid_foods_per_slot_count_matches_total_slots(self):
        aco = make_aco()
        assert len(aco.valid_foods_per_slot) == aco.total_slots

    def test_valid_foods_per_slot_non_empty(self):
        aco = make_aco()
        for slot, valid in enumerate(aco.valid_foods_per_slot):
            assert len(valid) > 0, f"Slot {slot} has no valid foods"

    def test_pheromone_starts_as_none(self):
        aco = make_aco()
        assert aco.pheromone is None


# ── _initialize ──────────────────────────────────────────────────────────────

class TestInitialize:

    def test_pheromone_shape_after_initialize(self):
        aco = make_aco()
        aco._initialize()
        assert aco.pheromone.shape == (aco.total_slots, aco.n_foods)

    def test_pheromone_starts_at_one(self):
        aco = make_aco()
        aco._initialize()
        assert np.all(aco.pheromone == 1.0)

    def test_best_fitness_starts_at_infinity(self):
        aco = make_aco()
        aco._initialize()
        assert aco.best_fitness == float("inf")

    def test_histories_start_empty(self):
        aco = make_aco()
        aco._initialize()
        assert aco.pheromone_history == []
        assert aco.best_fitness_history == []


# ── _construct_solution ──────────────────────────────────────────────────────

class TestConstructSolution:

    def test_returns_lists_of_correct_length(self):
        aco = make_aco()
        aco._initialize()
        foods, amounts = aco._construct_solution()
        assert len(foods) == aco.total_slots
        assert len(amounts) == aco.total_slots

    def test_foods_are_within_valid_per_slot(self):
        aco = make_aco()
        aco._initialize()
        foods, _ = aco._construct_solution()
        for slot, food_idx in enumerate(foods):
            valid = aco.valid_foods_per_slot[slot]
            assert food_idx in valid, f"Slot {slot}: food {food_idx} not in valid set"

    def test_amounts_within_bounds(self):
        aco = make_aco()
        aco._initialize()
        for _ in range(5):
            _, amounts = aco._construct_solution()
            assert all(0.1 <= a <= 5.0 for a in amounts)

    def test_foods_are_integers(self):
        aco = make_aco()
        aco._initialize()
        foods, _ = aco._construct_solution()
        assert all(isinstance(f, int) for f in foods)


# ── _evaluate ────────────────────────────────────────────────────────────────

class TestEvaluate:

    def test_matches_individual_calculate_fitness(self):
        aco = make_aco()
        aco._initialize()
        foods, amounts = aco._construct_solution()
        assert aco._evaluate(foods, amounts) == Individual.calculate_fitness(foods, amounts)

    def test_returns_non_negative(self):
        aco = make_aco()
        aco._initialize()
        foods, amounts = aco._construct_solution()
        assert aco._evaluate(foods, amounts) >= 0


# ── _update_pheromone ────────────────────────────────────────────────────────

class TestUpdatePheromone:

    def test_evaporation_reduces_pheromone(self):
        aco = make_aco(rho=0.1)
        aco._initialize()
        before = aco.pheromone.copy()
        aco._update_pheromone([])
        assert np.all(aco.pheromone < before)
        assert np.allclose(aco.pheromone, before * 0.9)

    def test_deposit_on_used_paths(self):
        aco = make_aco(rho=0.1)
        aco._initialize()
        foods = [int(aco.valid_foods_per_slot[slot][0]) for slot in range(aco.total_slots)]
        amounts = [1.0] * aco.total_slots
        aco._update_pheromone([(foods, amounts, 100.0)])
        for slot, used_food in enumerate(foods):
            other_foods = [f for f in aco.valid_foods_per_slot[slot] if f != used_food]
            if other_foods:
                assert aco.pheromone[slot, used_food] > aco.pheromone[slot, other_foods[0]]

    def test_infinite_fitness_trail_skipped(self):
        aco = make_aco(rho=0.0)
        aco._initialize()
        foods = [0] * aco.total_slots
        amounts = [1.0] * aco.total_slots
        aco._update_pheromone([(foods, amounts, float("inf"))])
        assert np.all(aco.pheromone == 1.0)

    def test_lower_fitness_means_larger_deposit(self):
        aco = make_aco(rho=0.0)
        aco._initialize()
        food_idx = int(aco.valid_foods_per_slot[0][0])
        foods_low = [food_idx] + [0] * (aco.total_slots - 1)
        foods_high = list(foods_low)
        amounts = [1.0] * aco.total_slots
        aco_low = make_aco(rho=0.0)
        aco_low._initialize()
        aco_low._update_pheromone([(foods_low, amounts, 10.0)])

        aco_high = make_aco(rho=0.0)
        aco_high._initialize()
        aco_high._update_pheromone([(foods_high, amounts, 1000.0)])

        assert aco_low.pheromone[0, food_idx] > aco_high.pheromone[0, food_idx]


# ── optimize (integration) ───────────────────────────────────────────────────

class TestOptimize:

    def test_returns_two_lists(self):
        aco = make_aco(n_ants=3)
        foods, amounts = aco.optimize(max_iterations=2)
        assert isinstance(foods, list)
        assert isinstance(amounts, list)

    def test_solution_length_matches_total_slots(self):
        aco = make_aco(n_ants=3)
        foods, amounts = aco.optimize(max_iterations=2)
        assert len(foods) == aco.total_slots
        assert len(amounts) == aco.total_slots

    def test_best_fitness_is_finite(self):
        aco = make_aco(n_ants=3)
        aco.optimize(max_iterations=2)
        assert aco.best_fitness < float("inf")

    def test_history_length_matches_iterations(self):
        aco = make_aco(n_ants=3)
        aco.optimize(max_iterations=4)
        assert len(aco.best_fitness_history) == 4
        assert len(aco.pheromone_history) == 4

    def test_best_fitness_monotone_non_increasing(self):
        aco = make_aco(n_ants=3)
        aco.optimize(max_iterations=5)
        history = aco.best_fitness_history
        for i in range(1, len(history)):
            assert history[i] <= history[i - 1], (
                f"Best fitness regressed at iteration {i}: "
                f"{history[i]} > {history[i - 1]}"
            )

    def test_solution_passes_individual_constraints(self):
        aco = make_aco(n_ants=3)
        foods, amounts = aco.optimize(max_iterations=2)
        # Building Individual should not raise (validates lengths internally)
        ind = Individual(foods, amounts)
        assert ind.fitness == aco.best_fitness
