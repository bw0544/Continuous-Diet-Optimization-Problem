import numpy as np
from copy import deepcopy

from data_models.database import FOOD_DATABASE
from data_models.individual import Individual
from data_models.subject import TEST_SUBJECT_JOHN


class ACOAlgorithm:

    def __init__(
            self,
            foods=FOOD_DATABASE,
            target_calories=TEST_SUBJECT_JOHN.daily_calories,
            n_ants=8,
            alpha=1,
            beta=4,
            rho=0.2
    ):

        self.foods = foods

        self.values = np.array([
            max(food["calorias"], 1)
            for food in foods
        ])

        self.weights = np.array([
            max(food["calorias"], 1)
            for food in foods
        ])

        self.max_capacity = target_calories

        self.n_ants = n_ants
        self.alpha = alpha
        self.beta = beta
        self.rho = rho

        self.pheromone = None

        self.best_solution = None
        self.best_fitness = float("-inf")

        self.pheromone_history = []
        self.trails_history = []
        self.best_fitness_history = []

    # ==========================================
    # MAIN
    # ==========================================

    def run(self, population_size=10, iterations=25):

        self._initialize()

        history = []

        n_evaluations = 0
        max_evaluations = iterations * self.n_ants

        iter_fitness = 1e-10

        iteration = 0

        while n_evaluations < max_evaluations:

            print(f"iteration {iteration + 1}")

            trails = []

            for _ in range(self.n_ants):

                solution = self._construct_solution()

                fitness = self._evaluate(solution)

                n_evaluations += 1

                trails.append((solution, fitness))

                if fitness > self.best_fitness:

                    self.best_solution = solution
                    self.best_fitness = fitness

            self._update_pheromone(
                trails,
                iter_fitness
            )

            iter_fitness = max(
                self.best_fitness,
                1e-10
            )

            self.trails_history.append(
                deepcopy(trails)
            )

            self.best_fitness_history.append(
                self.best_fitness
            )

            valid_fitness = [
                fit
                for _, fit in trails
                if np.isfinite(fit)
            ]

            history.append(
                {
                    "best_fitness": self.best_fitness,
                    "avg_fitness": (
                        np.mean(valid_fitness)
                        if len(valid_fitness) > 0
                        else 0
                    ),
                    "unique_foods": len(set(
                        food
                        for sol, _ in trails
                        for food in sol.foods
                    ))
                }
            )

            print(
                f"best fitness: "
                f"{self.best_fitness:.8f}"
            )

            iteration += 1

        return self.best_solution, history

    # ==========================================
    # INIT
    # ==========================================

    def _initialize(self):

        self.pheromone = np.ones(
            len(self.weights),
            dtype=float
        )

        self.best_solution = None
        self.best_fitness = float("-inf")

        self.pheromone_history = []
        self.trails_history = []
        self.best_fitness_history = []

    # ==========================================
    # EVALUATE
    # ==========================================

    def _evaluate(self, individual):

        total = 0

        for food_idx, amount in zip(
                individual.foods,
                individual.amounts
        ):

            total += (
                self.values[food_idx]
                * amount
            )

        target = self.max_capacity * 7

        difference = abs(
            target - total
        )

        return 1 / (
            1 + difference
        )

    # ==========================================
    # CONSTRUCT SOLUTION
    # ==========================================

    def _construct_solution(self):

        solution = np.zeros(
            len(self.weights),
            dtype=int
        )

        foods_vector = []
        amounts_vector = []

        max_foods = 11

        while np.sum(solution) < max_foods:

            candidates = self._get_candidates(
                solution
            )

            if len(candidates) == 0:
                break

            pheromones = np.power(
                np.maximum(
                    self.pheromone[candidates],
                    1e-10
                ),
                self.alpha
            )

            heuristic = np.power(
                np.maximum(
                    self._heuristic(candidates),
                    1e-10
                ),
                self.beta
            )

            scores = (
                pheromones * heuristic
            )

            scores = np.nan_to_num(
                scores,
                nan=1e-10,
                posinf=1e-10,
                neginf=1e-10
            )

            scores[scores < 0] = 0

            total = np.sum(scores)

            if total <= 0:

                probabilities = np.ones(
                    len(candidates)
                ) / len(candidates)

            else:

                probabilities = (
                    scores / total
                )

            probabilities = np.nan_to_num(
                probabilities,
                nan=0.0
            )

            probabilities[
                probabilities < 0
            ] = 0

            prob_sum = np.sum(
                probabilities
            )

            if prob_sum <= 0:

                probabilities = np.ones(
                    len(candidates)
                ) / len(candidates)

            else:

                probabilities /= prob_sum

            chosen = np.random.choice(
                candidates,
                p=probabilities
            )

            solution[chosen] = 1

        selected = np.argwhere(
            solution == 1
        ).flatten()

        if len(selected) < 11:

            remaining = [

                i for i in range(
                    len(self.weights)
                )

                if i not in selected

            ]

            extra = np.random.choice(
                remaining,
                size=11 - len(selected),
                replace=False
            )

            selected = np.concatenate([
                selected,
                extra
            ])

        for day in range(7):

            for idx in selected[:11]:

                foods_vector.append(
                    int(idx)
                )

                amounts_vector.append(
                    np.random.uniform(
                        0.3,
                        1.0
                    )
                )

        return Individual(
            foods_vector,
            amounts_vector
        )

    # ==========================================
    # HEURISTIC
    # ==========================================

    def _heuristic(self, candidates):

        weights = self.weights[
            candidates
        ].astype(float)

        weights[
            weights <= 0
        ] = 1

        heuristic = (
            self.values[candidates]
            / weights
        )

        heuristic = np.nan_to_num(
            heuristic,
            nan=1.0,
            posinf=1.0,
            neginf=1.0
        )

        heuristic[
            heuristic <= 0
        ] = 1e-10

        return heuristic

    # ==========================================
    # GET CANDIDATES
    # ==========================================

    def _get_candidates(
            self,
            solution
    ):

        selected = np.argwhere(
            solution == 1
        ).flatten()

        candidates = [

            i for i in range(
                len(self.weights)
            )

            if i not in selected

        ]

        return np.array(candidates)

    # ==========================================
    # UPDATE PHEROMONE
    # ==========================================

    def _update_pheromone(
            self,
            trails,
            best_fitness
    ):

        self.pheromone_history.append(
            self.pheromone.copy()
        )

        evaporation = max(
            1 - self.rho,
            0.01
        )

        self.pheromone *= evaporation

        for solution, fitness in trails:

            if not np.isfinite(
                    fitness
            ):
                continue

            delta_fitness = max(
                fitness,
                1e-10
            )

            used = set(
                solution.foods
            )

            for idx in used:

                self.pheromone[idx] += (
                    delta_fitness
                )

        self.pheromone = np.nan_to_num(
            self.pheromone,
            nan=1.0,
            posinf=1.0,
            neginf=1.0
        )

        self.pheromone[
            self.pheromone <= 0
        ] = 1e-10
