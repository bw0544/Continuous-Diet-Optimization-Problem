import random

from data_models.database import FOOD_DATABASE
from data_models.individual import Individual
from main_functionalities import MainFunctionalities
from wrapper_helper_functions import FoodCategory, filter_food

_MEAL_STRUCTURE = [3, 1, 3, 1, 3]
_CATEGORIES_PER_SLOT = [
    FoodCategory.BREAKFAST_DRINK, FoodCategory.BREAKFAST, FoodCategory.BREAKFAST,
    FoodCategory.SNACKS,
    FoodCategory.DRINKS, FoodCategory.LUNCH_OR_DINNER, FoodCategory.LUNCH_OR_DINNER,
    FoodCategory.SNACKS,
    FoodCategory.DRINKS, FoodCategory.LUNCH_OR_DINNER, FoodCategory.LUNCH_OR_DINNER,
]

FOODS_PER_DAY = 11
DAYS = 7
MEAL_SLOTS_PER_DAY = 5
TOTAL_MEAL_SLOTS = MEAL_SLOTS_PER_DAY * DAYS

AGE = 30
BLX_ALPHA = 0.5
P_DISCRETE = 0.05
P_CONTINUOUS = 0.1
P_RESET = 0.02
SIGMA = 0.3
LOCAL_SEARCH_INTERVAL = 10
LOCAL_SEARCH_ITERATIONS = 50
SIGMA_LS = 0.05
ELITE_SIZE = 2
TOURNAMENT_K = 3
SIMILARITY_THRESHOLD = 0.8


class GeneticAlgorithm:

    def run(self, population_size=100, iterations=500) -> tuple[Individual, list[dict]]:
        history = []
        population = _create_initial_population(population_size)

        for i in range(iterations):
            offspring_pool = _generate_offspring(population)

            if i % LOCAL_SEARCH_INTERVAL == 0:
                best = min(population, key=lambda ind: ind.fitness)
                offspring_pool.append(_local_search(best))

            population = _select_new_population(population, offspring_pool, population_size)
            history.append(_record_history(population))

        return min(population, key=lambda ind: ind.fitness), history


def _create_initial_population(population_size: int) -> list[Individual]:
    return [MainFunctionalities.create_random_individual() for _ in range(population_size)]


def _tournament_select(population: list[Individual], exclude: Individual = None) -> Individual:
    pool = [ind for ind in population if ind is not exclude]
    contestants = random.sample(pool, TOURNAMENT_K)
    return min(contestants, key=lambda ind: ind.fitness)


def _get_meal_slot_indices(meal_slot: int) -> list[int]:
    day = meal_slot // MEAL_SLOTS_PER_DAY
    meal_within_day = meal_slot % MEAL_SLOTS_PER_DAY
    day_start = day * FOODS_PER_DAY
    meal_start = sum(_MEAL_STRUCTURE[:meal_within_day])
    num_foods = _MEAL_STRUCTURE[meal_within_day]
    return list(range(day_start + meal_start, day_start + meal_start + num_foods))


def _crossover(parent_1: Individual, parent_2: Individual) -> Individual:
    foods = list(parent_1.foods)
    amounts = list(parent_1.amounts)

    for meal_slot in range(TOTAL_MEAL_SLOTS):
        indices = _get_meal_slot_indices(meal_slot)
        take_from_p2 = random.random() < 0.5

        for idx in indices:
            if take_from_p2:
                foods[idx] = parent_2.foods[idx]

            a1, a2 = parent_1.amounts[idx], parent_2.amounts[idx]
            lo, hi = min(a1, a2), max(a1, a2)
            spread = hi - lo
            new_amount = random.uniform(lo - BLX_ALPHA * spread, hi + BLX_ALPHA * spread)
            amounts[idx] = max(0.1, min(5.0, new_amount))

    return Individual(foods, amounts)


def _mutate(individual: Individual) -> Individual:
    foods = list(individual.foods)
    amounts = list(individual.amounts)

    for meal_slot in range(TOTAL_MEAL_SLOTS):
        indices = _get_meal_slot_indices(meal_slot)

        if random.random() < P_RESET:
            for idx in indices:
                category = _CATEGORIES_PER_SLOT[idx % FOODS_PER_DAY]
                valid_foods = filter_food(FOOD_DATABASE, category, AGE)
                foods[idx] = random.choice(valid_foods)
                amounts[idx] = random.uniform(0.1, 5.0)
            continue

        for idx in indices:
            category = _CATEGORIES_PER_SLOT[idx % FOODS_PER_DAY]

            if random.random() < P_DISCRETE:
                valid_foods = filter_food(FOOD_DATABASE, category, AGE)
                foods[idx] = random.choice(valid_foods)

            if random.random() < P_CONTINUOUS:
                amounts[idx] = max(0.1, min(5.0, amounts[idx] + random.gauss(0, SIGMA)))

    return Individual(foods, amounts)


def _generate_offspring(population: list[Individual]) -> list[Individual]:
    offspring = []

    for _ in range(80):
        parent_1 = _tournament_select(population)
        parent_2 = _tournament_select(population, exclude=parent_1)
        offspring.append(_mutate(_crossover(parent_1, parent_2)))

    for _ in range(15):
        offspring.append(_mutate(_tournament_select(population)))

    for _ in range(5):
        offspring.append(MainFunctionalities.create_random_individual())

    return offspring


def _is_too_similar(candidate: Individual, population: list[Individual]) -> bool:
    candidate_foods = set(candidate.foods)
    for individual in population:
        shared = len(candidate_foods & set(individual.foods))
        if shared / len(candidate_foods) >= SIMILARITY_THRESHOLD:
            return True
    return False


def _select_new_population(
    population: list[Individual],
    offspring_pool: list[Individual],
    population_size: int
) -> list[Individual]:
    elites = sorted(population, key=lambda ind: ind.fitness)[:ELITE_SIZE]
    new_population = list(elites)

    for candidate in sorted(offspring_pool, key=lambda ind: ind.fitness):
        if len(new_population) >= population_size:
            break
        if not _is_too_similar(candidate, new_population):
            new_population.append(candidate)

    for candidate in sorted(offspring_pool, key=lambda ind: ind.fitness):
        if len(new_population) >= population_size:
            break
        if candidate not in new_population:
            new_population.append(candidate)

    return new_population


def _local_search(individual: Individual) -> Individual:
    foods = list(individual.foods)
    amounts = list(individual.amounts)
    current_fitness = individual.fitness

    for _ in range(LOCAL_SEARCH_ITERATIONS):
        idx = random.randrange(len(amounts))
        new_amount = max(0.1, min(5.0, amounts[idx] + random.gauss(0, SIGMA_LS)))
        candidate_amounts = list(amounts)
        candidate_amounts[idx] = new_amount
        if Individual.calculate_fitness(foods, candidate_amounts) < current_fitness:
            amounts[idx] = new_amount
            current_fitness = Individual.calculate_fitness(foods, amounts)

        idx = random.randrange(len(foods))
        category = _CATEGORIES_PER_SLOT[idx % FOODS_PER_DAY]
        valid_foods = filter_food(FOOD_DATABASE, category, AGE)
        alternatives = [f for f in valid_foods if f != foods[idx]] or valid_foods
        new_food = random.choice(alternatives)
        candidate_foods = list(foods)
        candidate_foods[idx] = new_food
        if Individual.calculate_fitness(candidate_foods, amounts) < current_fitness:
            foods[idx] = new_food
            current_fitness = Individual.calculate_fitness(foods, amounts)

    return Individual(foods, amounts)


def _record_history(population: list[Individual]) -> dict:
    fitnesses = [ind.fitness for ind in population]
    unique_foods = len({food for ind in population for food in ind.foods})
    return {
        "best_fitness": min(fitnesses),
        "avg_fitness": sum(fitnesses) / len(fitnesses),
        "unique_foods": unique_foods,
    }
