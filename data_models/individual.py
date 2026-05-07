from dataclasses import dataclass

from data_models.database import FOOD_DATABASE
from data_models.subject import  TEST_SUBJECT_JOHN
from reference_code.constants import DIAS_SEMANA


@dataclass
class Individual:
    def __init__(self, foods: list[int] , amounts: list[float]):
        """
        :param foods: list of indices that indicate to the food database (e.g. 0 indicates first food in the database)
        :param amounts: list of amounts (varies from 0.1 to 5) to indicate the mutiplier for each food

        NOTE: both vectors MUST be of the same length
        """

        if len(foods) != len(amounts):
            raise ValueError(f"Foods and amounts vectors must be of the same length. Got: {len(foods)} and {len(amounts)}")

        self.foods = foods
        self.amounts = amounts
        self.fitness = self.calculate_fitness(foods, amounts)

    @staticmethod
    def calculate_fitness(foods, amounts):
        daily_calories_target = TEST_SUBJECT_JOHN.daily_calories
        target_differences = []

        foods_in_day = int(len(foods) / len(DIAS_SEMANA))

        for day_idx in range(7):
            daily_calories = 0

            for food_idx in range(foods_in_day):
                index = day_idx * foods_in_day + food_idx
                food_db_index = foods[index]
                food_info = FOOD_DATABASE[food_db_index]

                amount = amounts[index]
                current_food_calories = food_info['calorias'] * amount
                daily_calories += current_food_calories

            target_difference = abs(daily_calories_target - daily_calories)
            target_differences.append(target_difference)

        total_target_difference = sum(target_differences)
        return total_target_difference