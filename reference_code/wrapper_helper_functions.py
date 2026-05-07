from enum import Enum

from reference_code.helper_functions import filtrar_comida, traducir_solucion, calculo_macronutrientes


def calculate_macronutrients(proteins: float, carbohydrates: float, fats: float) -> tuple[float, float, float]:
    """
    Calculate the percentage of calories from each macronutrient.

    The function converts grams of proteins, carbohydrates, and fats into
    calories using standard nutritional values:

    - Proteins: 4 kcal per gram
    - Carbohydrates: 4 kcal per gram
    - Fats: 9 kcal per gram

    It then calculates the percentage contribution of each macronutrientto the total caloric intake.

    :param proteins: Amount of protein in grams.
    :param carbohydrates: Amount of carbohydrates in grams.
    :param fats: Amount of fat in grams.

    :returns:
        A tuple containing:
            - Percentage of calories from proteins.
            - Percentage of calories from carbohydrates.
            - Percentage of calories from fats.

    :example:

    >>> calculate_macronutrients(30, 50, 20)
    (24.0, 40.0, 36.0)"""

    return calculo_macronutrientes(proteins, carbohydrates, fats)





class FoodCategory(Enum):

    BREAKFAST = "desayuno"
    BREAKFAST_DRINK = "bebida_desayuno"
    LUNCH_OR_DINNER = "almuerzo_cena"
    DRINKS = "bebidas"
    SNACKS = "snacks"


def filter_food(food_database: list[dict], food_category: FoodCategory, age: int) -> list[int]:
    """
    Filter food items based on meal type and user age.

    :param food_database: List of food items.
    :param food_category: Type of meal or category to filter.
    :param age: Age of the user.

    :returns:
        List of indices of matching food items.
    :rtype:
        list[int]

    :example:

    >>> filter_food(food_database, "desayuno", 20)
    [0, 3, 8, 12]
    """
    return filtrar_comida(food_database, food_category.value, age)


def translate_solution(solution: list[int], food_database: list[dict]) -> tuple[dict, dict]:
    """
    Translate a numerical solution into a structured meal plan.

    The function maps food indices from the solution to food items,
    builds a weekly menu, and calculates daily nutritional values.

    :param solution: List of food indices representing the solution.
    :param comida_bd: List of available food items.

    :returns:
        A tuple containing:
            - The generated weekly menu.
            - Daily nutritional information.


    :example:

    :example:

    >>> solucion = [0, 2, 1]
    >>> comida_bd = [
    ...     {
    ...         "nombre": "Apple",
    ...         "grupo": "Fruits",
    ...         "calorias": 52,
    ...         "proteinas": 0.3,
    ...         "carbohidratos": 14,
    ...         "grasas": 0.2
    ...     },
    ...     {
    ...         "nombre": "Chicken Breast",
    ...         "grupo": "Meat",
    ...         "calorias": 165,
    ...         "proteinas": 31,
    ...         "carbohidratos": 0,
    ...         "grasas": 3.6
    ...     },
    ...     {
    ...         "nombre": "Rice",
    ...         "grupo": "Cereals",
    ...         "calorias": 130,
    ...         "proteinas": 2.7,
    ...         "carbohidratos": 28,
    ...         "grasas": 0.3
    ...     }
    ... ]
    >>>
    >>> menu, datos_dia = traducir_solucion(solucion, comida_bd)
    >>>
    >>> menu
    {
        "Monday": {
            "Breakfast": (
                ["- Apple (Fruits)", "- Rice (Cereals)"],
                182
            ),
            "Lunch": (
                ["- Chicken Breast (Meat)"],
                165
            )
        },
        "Tuesday": {...},
        ...
    }
    >>>
    >>> datos_dia
    {
        "Monday": {
            "calorias": 347,
            "proteinas": 34.0,
            "carbohidratos": 42,
            "grasas": 4.1,
            "porcentaje_proteinas": 39.2,
            "porcentaje_carbohidratos": 48.4,
            "porcentaje_grasas": 12.4
        },
        ...
    }
    """

    result_spanish, daily_nutritional_data = traducir_solucion(solution, food_database)


    weekdays_english = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekdays_spanish =  ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']
    weekdays_translations = dict(zip(weekdays_spanish, weekdays_english))

    meals_english = ['Breakfast', 'Morning Snack', 'Lunch', 'Afternoon Snack', 'Dinner']
    meals_spanish = ['Desayuno', 'Tentempie', 'Almuerzo', 'Merienda', 'Cena']
    meals_translations = dict(zip(meals_spanish, meals_english))

    # translating the weekly menu

    for weekday_es, weekday_en in weekdays_translations.items():
        result_spanish[weekday_en] = result_spanish[weekday_es].pop()

    for weekday_es, day_menu_es in result_spanish.items():
        for meal_es, meal_en in meals_translations.items():
            day_menu_es[meal_en] = day_menu_es[meal_es].pop()

    # translating the daily nutritional data



    return result_spanish

def translate_sol(solution: list[int], food_db: list[dict]) -> tuple[dict, dict]:


    WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    #MEALS = ['Breakfast', 'Morning Snack', 'Lunch', 'Afternoon Snack', 'Dinner']
    MEALS = [
        {"nombre": "Breakfast", "num_alimentos": 3},
        {"nombre": "Morning Snack", "num_alimentos": 1},
        {"nombre": "Lunch", "num_alimentos": 3},
        {"nombre": "Afternoon Snack", "num_alimentos": 1},
        {"nombre": "Dinner", "num_alimentos": 3}
    ]

    menu = {}
    daily_data = {day: {"calories": 0, "proteins": 0, "carbohydrates": 0, "fats": 0} for day in WEEKDAYS}

    indice = 0
    for dia in WEEKDAYS:
        menu[dia] = {}

        for comida in MEALS:
            num_alimentos = comida["num_alimentos"]
            alimentos = []
            calorias_totales = 0

            for _ in range(num_alimentos):

                if indice < len(solution):
                    idx = int(solution[indice])
                    alimento = food_db[idx]
                    nombre_completo = f"- {alimento['nombre']} ({alimento['grupo']})"
                    alimentos.append(nombre_completo)

                    calorias_totales += alimento["calorias"]
                    daily_data[dia]["calories"] += alimento["calorias"]
                    daily_data[dia]["proteins"] += alimento["proteinas"]
                    daily_data[dia]["carbohydrates"] += alimento["carbohidratos"]
                    daily_data[dia]["fats"] += alimento["grasas"]

                    indice += 1

            menu[dia][comida["nombre"]] = (alimentos, calorias_totales)

    for dia in WEEKDAYS:
        calorias = daily_data[dia]["calories"]

        if calorias > 0:
            daily_data[dia]["percentage_proteins"], daily_data[dia]["percentage_carbohydrates"], daily_data[dia][
                "percentage_fats"] = \
                calculo_macronutrientes(daily_data[dia]["calories"], daily_data[dia]["carbohydrates"],
                                        daily_data[dia]["fats"])
        else:
            daily_data[dia]["percentage_proteins"] = daily_data[dia]["percentage_carbohydrates"] = daily_data[dia][
                "percentage_fats"] = 0

    return menu, daily_data


if __name__ == "__main__":
    # Example food database
    food_db = [
        {"nombre": "Apple", "grupo": "Fruits", "calorias": 52, "proteinas": 0.3, "carbohidratos": 14, "grasas": 0.2},
        {"nombre": "Chicken Breast", "grupo": "Meat", "calorias": 165, "proteinas": 31, "carbohidratos": 0, "grasas": 3.6},
        {"nombre": "Rice", "grupo": "Cereals", "calorias": 130, "proteinas": 2.7, "carbohidratos": 28, "grasas": 0.3},
        {"nombre": "Banana", "grupo": "Fruits", "calorias": 89, "proteinas": 1.1, "carbohidratos": 23, "grasas": 0.3},
        {"nombre": "Egg", "grupo": "Protein", "calorias": 155, "proteinas": 13, "carbohidratos": 1.1, "grasas": 11}
    ]

    # Example solution (indices into food_db)
    solution = [i % 5 for i in range(77)]

    # Call function
    menu, daily_data = translate_sol(solution, food_db)

    # Print results
    print("MENU:\n")
    for day, meals in menu.items():
        print(day, "->", meals)

    print("\nDAILY DATA:\n")
    for day, data in daily_data.items():
        print(day, "->", data)