import os
import sys

import numpy as np

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


class ACOFoodOptimizer:

    def __init__(
            self,
            foods=None,
            target_calories=None,
            n_ants=30,
            alpha=1,
            beta=3,
            rho=0.1
    ):
        from data_models.database import FOOD_DATABASE
        from data_models.subject import TEST_SUBJECT_JOHN
        from genetic_algorithm.genetic_algorithm import (
            FOODS_PER_DAY,
            DAYS,
            _CATEGORIES_PER_SLOT,
            AGE,
        )
        from wrapper_helper_functions import filter_food

        self.foods = foods if foods is not None else FOOD_DATABASE

        self.calories = np.array([food["calorias"] for food in self.foods])

        self.target_calories = (
            target_calories if target_calories is not None
            else TEST_SUBJECT_JOHN.daily_calories
        )

        self.n_ants = n_ants
        self.alpha = alpha
        self.beta = beta
        self.rho = rho

        self.foods_per_day = FOODS_PER_DAY
        self.days = DAYS
        self.total_slots = FOODS_PER_DAY * DAYS
        self.age = AGE
        self.categories_per_slot = _CATEGORIES_PER_SLOT

        self.valid_foods_per_slot = [
            np.array(
                filter_food(
                    self.foods,
                    self.categories_per_slot[slot % self.foods_per_day],
                    self.age
                )
            )
            for slot in range(self.total_slots)
        ]

        self.n_foods = len(self.foods)
        self.pheromone = None

        self.best_solution = None
        self.best_amounts = None
        self.best_fitness = float("inf")

        self.pheromone_history = []
        self.best_fitness_history = []

    # =====================================
    # MAIN OPTIMIZATION
    # =====================================

    def optimize(self, max_iterations=100):

        self._initialize()

        for iteration in range(max_iterations):

            trails = []

            for ant in range(self.n_ants):

                foods, amounts = self._construct_solution()

                fitness = self._evaluate(foods, amounts)

                trails.append((foods, amounts, fitness))

                if fitness < self.best_fitness:

                    self.best_fitness = fitness
                    self.best_solution = list(foods)
                    self.best_amounts = list(amounts)

            self._update_pheromone(trails)

            self.pheromone_history.append(self.pheromone.copy())

            self.best_fitness_history.append(self.best_fitness)

            print(
                f"iteration {iteration + 1}/{max_iterations}"
                f" | best fitness: {self.best_fitness:.2f}"
            )

        return self.best_solution, self.best_amounts

    # =====================================
    # INITIALIZE
    # =====================================

    def _initialize(self):

        self.pheromone = np.ones((self.total_slots, self.n_foods))

        self.best_solution = None
        self.best_amounts = None
        self.best_fitness = float("inf")

        self.pheromone_history = []
        self.best_fitness_history = []

    # =====================================
    # FITNESS
    # =====================================

    def _evaluate(self, foods, amounts):

        from data_models.individual import Individual

        return Individual.calculate_fitness(foods, amounts)

    # =====================================
    # CONSTRUCT SOLUTION
    # =====================================

    def _construct_solution(self):

        foods = [0] * self.total_slots
        amounts = [0.0] * self.total_slots

        target_per_food = self.target_calories / self.foods_per_day

        for slot in range(self.total_slots):

            candidates = self.valid_foods_per_slot[slot]

            pheromones = (
                self.pheromone[slot, candidates]
                ** self.alpha
            )

            heuristic = (
                1 / (1 + np.abs(
                    self.calories[candidates]
                    - target_per_food
                ))
            ) ** self.beta

            probabilities = pheromones * heuristic

            probabilities = probabilities / probabilities.sum()

            chosen = np.random.choice(
                candidates,
                p=probabilities
            )

            foods[slot] = int(chosen)
            amounts[slot] = float(np.random.uniform(0.1, 5.0))

        return foods, amounts

    # =====================================
    # UPDATE PHEROMONES
    # =====================================

    def _update_pheromone(self, trails):

        # evaporation
        self.pheromone *= (1 - self.rho)

        for foods, amounts, fitness in trails:

            if fitness == float("inf"):
                continue

            deposit = 1 / (1 + fitness)

            for slot, food_idx in enumerate(foods):
                self.pheromone[slot, food_idx] += deposit
