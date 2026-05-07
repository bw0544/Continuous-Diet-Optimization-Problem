import random
from types import GeneratorType

from data_models.individual import Individual
from main_functionalities import MainFunctionalities


class GeneticAlgorithm:

    @staticmethod
    def create_initial_population(population_size) -> list[Individual]:
        return [MainFunctionalities.create_random_individual() for _ in range(population_size)]

    @staticmethod
    def choose_parent_tournament(population: list[Individual], tournament_size) -> Individual:
        """
        :param population: population of all individuals
        :param tournament_size: parameter for tournament selection, indicating how many individuals to randomly sample from the
         population and choose the best one as parent (value 3 is well-tested in the literature)
        :return: the selected individual
        """
        individuals_for_tournament = [random.choice(population) for _ in range(tournament_size)]
        best_individual = min(individuals_for_tournament, key=lambda individual: individual.fitness)
        return best_individual


    @staticmethod
    def uniform_crossover(parent1, parent2):
        """
        Applying crossover, creating an offspring from both parents.
        :param parent1: first parent
        :param parent2: second parent
        :return: new offpring
        """
        foods1, amounts1 = parent1.foods, parent1.amounts
        foods2, amounts2 = parent2.foods, parent2.amounts

        new_foods = []
        new_amounts = []

        for i in range(len(foods1)):
            if random.random() < 0.5:
                new_foods.append(foods1[i])
                new_amounts.append(amounts1[i])
            else:
                new_foods.append(foods2[i])
                new_amounts.append(amounts2[i])

        return Individual(new_foods, new_amounts)

    @staticmethod
    def create_offsprings_from_parents(population: list[Individual], offspring_num, tournament_size) -> list[Individual]:
        offsprings = []
        for _ in range(offspring_num):
            parents = [GeneticAlgorithm.choose_parent_tournament(population=population, tournament_size=tournament_size) for _ in range(2)]
            offspring = GeneticAlgorithm.uniform_crossover(*parents)
            #TODO: add mutation here
            offsprings.append(offspring)

        return offsprings


    @staticmethod
    def run(population_size=100, iterations=500, tournament_size=3):

        history = []
        population = GeneticAlgorithm.create_initial_population(population_size)

        for _ in range(iterations):
            offsprings = GeneticAlgorithm.create_offsprings_from_parents(population,
                                                             offspring_num=population_size,
                                                             tournament_size=tournament_size)
            pass



        #NOTE:  apply crossover -> uniform/multi-slot crossover (Meal-slot level crossover vs. food-slot level crossover)
        #       Structural level — uniform crossover at the meal slot level. Decides which parent each slot comes from
        #       Amount level — apply BLX-α to the amounts of the selected slots rather than just copying them directly

        #TODO:  apply mutation ->
        #       Discrete mutation: replace a food with another valid food from the same category
        #       Continuous mutation: nudge the amount with Gaussian noise, clamp to [0.1, 5.0]
        # .
        #          For each of the 35 meal slots:
        #              With p_discrete → swap food for valid food in same category
        #              With p_continuous → nudge amount with N(0, σ(t))
        # .
        #          For each of the 35 meals:
        #              With p_reset → completely reinitialize this meal randomly

        #TODO:   choose new population, based on fitness
        #         fitness: calories shortfall
        # .
        #         Choosing new population:
        #           1. Always keep top E=2 individuals (elitism — never lose best solution)
        #           2. Fill remaining N-2 spots from offspring
        #           3. But before adding an offspring, check if a very similar individual
        #              already exists in new population — if so, keep the more diverse one
        # .
        #           Could try as well:
        #           Current population:  100 individuals
        #               ↓
        #           Select 2 elites → carry forward unchanged
        #               ↓
        #           Generate offspring:
        #               - 80 via tournament selection + crossover + mutation
        #               - 15 via mutation only (no crossover)
        #               - 5  completely random valid solutions
        #               ↓
        #           New population:  2 elites + 98 best offspring = 100


        #TODO:  each n-th iteration apply local search
        # Amount tuning (continuous)
        # Food swap (discrete)
        # def local_search(solution, n_iterations=50, σ_ls=0.1):
        # .
        # for iteration in range(n_iterations):
        #    .
        #     # Phase 1 — try improving one random amount
        #     slot = random_slot()
        #     old_amount = solution[slot].amount
        #     new_amount = clamp(old_amount + N(0, σ_ls), 0.1, 5.0)
        #     .
        #     if fitness(solution with new_amount) < fitness(solution):
        #         solution[slot].amount = new_amount
        #     .
        #     # Phase 2 — try swapping one random food
        #     slot = random_slot()
        #     old_food = solution[slot].food
        #     new_food = random_choice(valid_pool[slot] - {old_food})
        #     .
        #     if fitness(solution with new_food) < fitness(solution):
        #         solution[slot].food = new_food
        # .
        # return solution


        #TODO: track history:
        # - best fitness in population
        # - average fitness in population
        # - population diversity (e.g. number of unique foods across population)
        # - whether local search fired this generation and by how much it improved

        pass

if __name__ == '__main__':
    GeneticAlgorithm.run()