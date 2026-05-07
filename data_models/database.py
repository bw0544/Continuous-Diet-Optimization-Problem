import json

def get_food_db():
    with open("../data_json/food.json", "r") as file:
        return json.load(file)

FOOD_DATABASE = get_food_db()