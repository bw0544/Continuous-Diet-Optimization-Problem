import random
import pytest

from data_models.database import FOOD_DATABASE
from data_models.individual import Individual
from data_models.subject import TEST_SUBJECT_JOHN
from main_functionalities import MainFunctionalities
from wrapper_helper_functions import FoodCategory, filter_food, calculate_macronutrients
from genetic_algorithm.genetic_algorithm import (
    _crossover,
    _mutate,
    _tournament_select,
    _get_meal_slot_indices,
    _generate_offspring,
    _select_new_population,
    _local_search,
    _is_too_similar,
    _record_history,
    FOODS_PER_DAY,
    DAYS,
    TOTAL_MEAL_SLOTS,
    MEAL_SLOTS_PER_DAY,
    _MEAL_STRUCTURE,
)


# ── helpers ──────────────────────────────────────────────────────────────────

def make_individual():
    return MainFunctionalities.create_random_individual()


def make_population(n=10):
    return [make_individual() for _ in range(n)]


# ── Individual ────────────────────────────────────────────────────────────────

class TestIndividual:

    def test_creates_with_correct_lengths(self):
        ind = make_individual()
        assert len(ind.foods) == FOODS_PER_DAY * DAYS
        assert len(ind.amounts) == FOODS_PER_DAY * DAYS

    def test_fitness_is_non_negative(self):
        ind = make_individual()
        assert ind.fitness >= 0

    def test_mismatched_lengths_raise(self):
        with pytest.raises(ValueError):
            Individual([0], [1.0, 2.0])

    def test_fitness_zero_when_calories_match_target(self):
        target = TEST_SUBJECT_JOHN.daily_calories
        foods_per_week = FOODS_PER_DAY * DAYS
        foods = [0] * foods_per_week
        cal_per_food = FOOD_DATABASE[0]['calorias']
        amount = target / (FOODS_PER_DAY * cal_per_food)
        amounts = [amount] * foods_per_week
        ind = Individual(foods, amounts)
        assert ind.fitness == pytest.approx(0.0, abs=1e-3)

    def test_calculate_fitness_matches_stored_fitness(self):
        ind = make_individual()
        recalculated = Individual.calculate_fitness(ind.foods, ind.amounts)
        assert ind.fitness == pytest.approx(recalculated)


# ── MainFunctionalities ───────────────────────────────────────────────────────

class TestMainFunctionalities:

    def test_create_random_individual_returns_individual(self):
        ind = MainFunctionalities.create_random_individual()
        assert isinstance(ind, Individual)

    def test_create_random_individual_has_77_foods(self):
        ind = MainFunctionalities.create_random_individual()
        assert len(ind.foods) == 77

    def test_amounts_within_bounds(self):
        ind = MainFunctionalities.create_random_individual()
        assert all(0.1 <= a <= 5.0 for a in ind.amounts)

    def test_get_food_info_returns_english_keys(self):
        info = MainFunctionalities.get_food_info(0)
        for key in ("name", "group", "calories", "fats", "proteins", "carbohydrates"):
            assert key in info


# ── filter_food ───────────────────────────────────────────────────────────────

class TestFilterFood:

    def test_returns_list_of_ints(self):
        result = filter_food(FOOD_DATABASE, FoodCategory.BREAKFAST, 25)
        assert isinstance(result, list)
        assert all(isinstance(i, int) for i in result)

    def test_indices_within_database_range(self):
        result = filter_food(FOOD_DATABASE, FoodCategory.LUNCH_OR_DINNER, 30)
        assert all(0 <= i < len(FOOD_DATABASE) for i in result)

    def test_non_empty_for_each_category(self):
        for category in FoodCategory:
            result = filter_food(FOOD_DATABASE, category, 30)
            assert len(result) > 0, f"No foods found for category {category}"


# ── calculate_macronutrients ─────────────────────────────────────────────────

class TestCalculateMacronutrients:

    def test_percentages_sum_to_100(self):
        p, c, f = calculate_macronutrients(30, 50, 20)
        assert p + c + f == pytest.approx(100.0, abs=1e-3)

    def test_known_values(self):
        p, c, f = calculate_macronutrients(30, 50, 20)
        assert p == pytest.approx(24.0, abs=0.1)
        assert c == pytest.approx(40.0, abs=0.1)
        assert f == pytest.approx(36.0, abs=0.1)

    def test_all_protein(self):
        p, c, f = calculate_macronutrients(100, 0, 0)
        assert p == pytest.approx(100.0, abs=0.1)
        assert c == pytest.approx(0.0, abs=0.1)
        assert f == pytest.approx(0.0, abs=0.1)


# ── _get_meal_slot_indices ────────────────────────────────────────────────────

class TestGetMealSlotIndices:

    def test_first_slot_starts_at_zero(self):
        assert _get_meal_slot_indices(0)[0] == 0

    def test_slot_size_matches_meal_structure(self):
        for slot in range(TOTAL_MEAL_SLOTS):
            indices = _get_meal_slot_indices(slot)
            meal_within_day = slot % MEAL_SLOTS_PER_DAY
            assert len(indices) == _MEAL_STRUCTURE[meal_within_day]

    def test_no_overlap_between_slots_in_same_day(self):
        all_indices = []
        for slot in range(MEAL_SLOTS_PER_DAY):
            all_indices.extend(_get_meal_slot_indices(slot))
        assert len(all_indices) == len(set(all_indices))

    def test_covers_full_week(self):
        all_indices = set()
        for slot in range(TOTAL_MEAL_SLOTS):
            all_indices.update(_get_meal_slot_indices(slot))
        assert all_indices == set(range(FOODS_PER_DAY * DAYS))


# ── _crossover ────────────────────────────────────────────────────────────────

class TestCrossover:

    def test_returns_individual(self):
        p1, p2 = make_individual(), make_individual()
        child = _crossover(p1, p2)
        assert isinstance(child, Individual)

    def test_child_same_length_as_parents(self):
        p1, p2 = make_individual(), make_individual()
        child = _crossover(p1, p2)
        assert len(child.foods) == len(p1.foods)
        assert len(child.amounts) == len(p1.amounts)

    def test_child_amounts_within_bounds(self):
        p1, p2 = make_individual(), make_individual()
        for _ in range(5):
            child = _crossover(p1, p2)
            assert all(0.1 <= a <= 5.0 for a in child.amounts)

    def test_child_foods_come_from_parents(self):
        p1, p2 = make_individual(), make_individual()
        child = _crossover(p1, p2)
        valid = set(p1.foods) | set(p2.foods)
        assert all(f in valid for f in child.foods)


# ── _mutate ───────────────────────────────────────────────────────────────────

class TestMutate:

    def test_returns_individual(self):
        ind = make_individual()
        mutated = _mutate(ind)
        assert isinstance(mutated, Individual)

    def test_mutated_lengths_unchanged(self):
        ind = make_individual()
        mutated = _mutate(ind)
        assert len(mutated.foods) == len(ind.foods)
        assert len(mutated.amounts) == len(ind.amounts)

    def test_mutated_amounts_within_bounds(self):
        ind = make_individual()
        for _ in range(5):
            mutated = _mutate(ind)
            assert all(0.1 <= a <= 5.0 for a in mutated.amounts)


# ── _tournament_select ────────────────────────────────────────────────────────

class TestTournamentSelect:

    def test_returns_individual_from_population(self):
        pop = make_population(10)
        selected = _tournament_select(pop)
        assert selected in pop

    def test_exclude_removes_individual(self):
        pop = make_population(10)
        excluded = pop[0]
        for _ in range(20):
            selected = _tournament_select(pop, exclude=excluded)
            assert selected is not excluded


# ── _generate_offspring ───────────────────────────────────────────────────────

class TestGenerateOffspring:

    def test_returns_100_offspring(self):
        pop = make_population(10)
        offspring = _generate_offspring(pop)
        assert len(offspring) == 100

    def test_all_offspring_are_individuals(self):
        pop = make_population(10)
        offspring = _generate_offspring(pop)
        assert all(isinstance(o, Individual) for o in offspring)


# ── _select_new_population ────────────────────────────────────────────────────

class TestSelectNewPopulation:

    def test_new_population_correct_size(self):
        pop = make_population(10)
        offspring = _generate_offspring(pop)
        new_pop = _select_new_population(pop, offspring, 10)
        assert len(new_pop) == 10

    def test_elites_are_preserved(self):
        pop = make_population(10)
        best = min(pop, key=lambda ind: ind.fitness)
        offspring = _generate_offspring(pop)
        new_pop = _select_new_population(pop, offspring, 10)
        assert best in new_pop


# ── _is_too_similar ───────────────────────────────────────────────────────────

class TestIsTooSimilar:

    def test_identical_individual_is_too_similar(self):
        ind = make_individual()
        assert _is_too_similar(ind, [ind])

    def test_empty_population_is_not_too_similar(self):
        ind = make_individual()
        assert not _is_too_similar(ind, [])


# ── _local_search ─────────────────────────────────────────────────────────────

class TestLocalSearch:

    def test_returns_individual(self):
        ind = make_individual()
        result = _local_search(ind)
        assert isinstance(result, Individual)

    def test_local_search_does_not_worsen_much(self):
        random.seed(42)
        ind = make_individual()
        result = _local_search(ind)
        assert result.fitness <= ind.fitness * 1.05


# ── _record_history ───────────────────────────────────────────────────────────

class TestRecordHistory:

    def test_record_has_required_keys(self):
        pop = make_population(5)
        record = _record_history(pop)
        assert "best_fitness" in record
        assert "avg_fitness" in record
        assert "unique_foods" in record

    def test_best_fitness_le_avg_fitness(self):
        pop = make_population(5)
        record = _record_history(pop)
        assert record["best_fitness"] <= record["avg_fitness"]