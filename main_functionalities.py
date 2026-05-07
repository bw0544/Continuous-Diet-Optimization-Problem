import json
import random

from data_models.individual import Individual
from reference_code.constants import DIAS_SEMANA
from wrapper_helper_functions import FoodCategory, filter_food


class MainFunctionalities:
    """
    This class includes all the important functions for operations shared
    between GeneticAlgorithm and Swarm Optimization.
    """
    @staticmethod
    def get_food_db():
        with open("data_json/food.json", "r") as file:
            return json.load(file)

    @staticmethod
    def create_random_individual() -> Individual:

        foods = []
        amounts = []

        categories = [FoodCategory.BREAKFAST_DRINK, FoodCategory.BREAKFAST, FoodCategory.BREAKFAST,
                      FoodCategory.SNACKS,
                      FoodCategory.DRINKS, FoodCategory.LUNCH_OR_DINNER, FoodCategory.LUNCH_OR_DINNER,
                      FoodCategory.SNACKS,
                      FoodCategory.DRINKS, FoodCategory.LUNCH_OR_DINNER, FoodCategory.LUNCH_OR_DINNER]

        for i in range(len(DIAS_SEMANA)):
            daily_food = []
            daily_amount = []
            for category in categories:
                foods_from_category = filter_food(PopulationManager.FOOD_DB, category, 30)
                daily_food.append(random.choice(foods_from_category))  # age should be once defined
                daily_amount.append(random.uniform(0.1, 5))

            foods.extend(daily_food)
            amounts.extend(daily_amount)

        return Individual(foods, amounts)

    @staticmethod
    def get_fitness_value(individual: Individual) -> float:
        raise NotImplementedError()

    @staticmethod
    def get_food_info(index: int) -> dict:
        result_es = MainFunctionalities.get_food_db()[index]
        result_en = {
            "name": result_es["nombre"],
            "group": result_es["grupo"],
            "calories": result_es["calorias"],
            "fats": result_es["grasas"],
            "proteins": result_es["proteinas"],
            "carbohydrates": result_es["carbohidratos"]
        }
        return result_en
