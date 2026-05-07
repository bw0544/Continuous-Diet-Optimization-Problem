from dataclasses import dataclass

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

