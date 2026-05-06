# note: this code takes the .json file as input data and does not depend on the mySQL connection

import json

from constants import GruposComida, DIAS_SEMANA, COMIDAS

with open("../data_json/food.json", "r") as file:
    comida_bd = json.load(file)


def calculo_macronutrientes(proteinas, carbohidratos, grasas):
    """Calcula el porcentaje de calorias provenientes de cada macronutriente."""

    calorias_proteinas = proteinas * 4
    calorias_carbohidratos = carbohidratos * 4
    calorias_grasas = grasas * 9

    total_calorias_macronutrientes = calorias_proteinas + calorias_carbohidratos + calorias_grasas

    porcentaje_proteinas = (calorias_proteinas / total_calorias_macronutrientes) * 100
    porcentaje_carbohidratos = (calorias_carbohidratos / total_calorias_macronutrientes) * 100
    porcentaje_grasas = (calorias_grasas / total_calorias_macronutrientes) * 100

    return porcentaje_proteinas, porcentaje_carbohidratos, porcentaje_grasas


def filtrar_comida(comida_bd, tipo, edad):
    """Filtra los alimentos segun el tipo de comida y la edad del usuario."""

    match tipo:
        case "almuerzo_cena":
            return [
                i for i, item in enumerate(comida_bd) if not item["grupo"].startswith(
                    (
                        GruposComida.Frutas.JUGOS_DE_FRUTAS[0],  # "FC"
                        GruposComida.Frutas.ZUMOS[0],  # "FE"
                        GruposComida.Bebidas.BEBIDAS[0],  # "P"
                        GruposComida.Alcohol.ALCOHOL[0],  # "Q"
                        GruposComida.Lacteos.LecheVaca.LECHE_VACA[0],  # "BA"
                        GruposComida.Lacteos.BEBIDAS_LACTEAS[0],  # "BH"
                        GruposComida.Bebidas.BebidasEnPolvoEsenciasInfusiones.BEBIDAS_EN_POLVO_ESENCIAS_INFUSIONES[0],
                        # "PA"
                        GruposComida.Azucares.AZUCARES[0],  # "S"
                        GruposComida.Cereales.CEREALES[0]  # "A"
                    )
                ) or item["grupo"] in {
                                                             GruposComida.Cereales.ARROZ[0],  # "AC"
                                                             GruposComida.Cereales.PASTA[0],  # "AD"
                                                             GruposComida.Cereales.PIZZAS[0],  # "AE"
                                                             GruposComida.Cereales.PANES[0]  # "AF"
                                                         }
            ]

        case "bebidas":
            bebidas = [
                i for i, item in enumerate(comida_bd) if item["grupo"].startswith(
                    (
                        GruposComida.Bebidas.BEBIDAS[0],  # "P"
                        GruposComida.Frutas.JUGOS_DE_FRUTAS[0],  # "FC"
                        GruposComida.Frutas.ZUMOS[0]  # "FE"
                    )
                ) and not item["grupo"].startswith(
                    GruposComida.Bebidas.BebidasEnPolvoEsenciasInfusiones.BEBIDAS_EN_POLVO_ESENCIAS_INFUSIONES[0]
                    # "PA"
                )
            ]
            if edad >= 18:
                bebidas_alcoholicas = [
                    i for i, item in enumerate(comida_bd) if item["grupo"].startswith(
                        GruposComida.Alcohol.ALCOHOL[0]  # "Q"
                    )
                ]
                bebidas.extend(bebidas_alcoholicas)
            return bebidas

        case "desayuno":
            return [
                i for i, item in enumerate(comida_bd) if item["grupo"].startswith(
                    (
                        GruposComida.Cereales.CEREALES[0],  # "A"
                        GruposComida.Huevos.HUEVOS[0],  # "C"
                        GruposComida.Frutas.FRUTAS_GENERALES[0],  # "FA"
                        GruposComida.Carne.CarneGeneral.BACON[0]  # "MAA"
                    )
                ) and item["grupo"] not in {
                                                             GruposComida.Cereales.ARROZ[0],  # "AC"
                                                             GruposComida.Cereales.PASTA[0],  # "AD"
                                                             GruposComida.Cereales.PIZZAS[0]  # "AE"
                                                         }
            ]

        case "bebida_desayuno":
            return [
                i for i, item in enumerate(comida_bd) if item["grupo"].startswith(
                    (
                        GruposComida.Lacteos.LecheVaca.LECHE_VACA[0],  # "BA"
                        GruposComida.Lacteos.BEBIDAS_LACTEAS[0],  # "BH"
                        GruposComida.Bebidas.BebidasEnPolvoEsenciasInfusiones.BEBIDAS_EN_POLVO_ESENCIAS_INFUSIONES[0],
                        # "PA"
                        GruposComida.Frutas.ZUMOS[0],  # "FE"
                        GruposComida.Frutas.JUGOS_DE_FRUTAS[0]  # "FC"
                    )
                )
            ]

        case "snacks":
            return [
                i for i, item in enumerate(comida_bd) if item["grupo"].startswith(
                    (
                        GruposComida.Frutas.FRUTAS[0],  # "F"
                        GruposComida.Azucares.AZUCARES[0]  # "S"
                    )
                )
            ]


def traducir_solucion(solucion, comida_bd):
    """Convierte la solucion de numeros en una lista de alimentos con sus nutrientes"""

    menu = {}
    datos_dia = {dia: {"calorias": 0, "proteinas": 0, "carbohidratos": 0, "grasas": 0} for dia in DIAS_SEMANA}

    indice = 0
    for dia in DIAS_SEMANA:
        menu[dia] = {}

        for comida in COMIDAS:
            num_alimentos = comida["num_alimentos"]
            alimentos = []
            calorias_totales = 0

            for _ in range(num_alimentos):

                # Traduce el indice a un alimento concreto
                if indice < len(solucion):
                    idx = int(solucion[indice])
                    alimento = comida_bd[idx]
                    nombre_completo = f"- {alimento['nombre']} ({alimento['grupo']})"
                    alimentos.append(nombre_completo)

                    # Suma las calorias y macronutrientes del alimento
                    calorias_totales += alimento["calorias"]
                    datos_dia[dia]["calorias"] += alimento["calorias"]
                    datos_dia[dia]["proteinas"] += alimento["proteinas"]
                    datos_dia[dia]["carbohidratos"] += alimento["carbohidratos"]
                    datos_dia[dia]["grasas"] += alimento["grasas"]

                    indice += 1

            menu[dia][comida["nombre"]] = (alimentos, calorias_totales)

    # Calcula los porcentajes de macronutrientes para cada dia
    for dia in DIAS_SEMANA:
        calorias = datos_dia[dia]["calorias"]

        if calorias > 0:
            datos_dia[dia]["porcentaje_proteinas"], datos_dia[dia]["porcentaje_carbohidratos"], datos_dia[dia][
                "porcentaje_grasas"] = \
                calculo_macronutrientes(datos_dia[dia]["proteinas"], datos_dia[dia]["carbohidratos"],
                                        datos_dia[dia]["grasas"])
        else:
            datos_dia[dia]["porcentaje_proteinas"] = datos_dia[dia]["porcentaje_carbohidratos"] = datos_dia[dia][
                "porcentaje_grasas"] = 0

    return menu, datos_dia

if __name__ == "__main__":

    # --- Test calculo_macronutrientes ---
    print("=== calculo_macronutrientes ===")
    proteinas, carbos, grasas = 150, 200, 70
    resultado_macros = calculo_macronutrientes(proteinas, carbos, grasas)
    print(f"Input:  {proteinas}g protein, {carbos}g carbs, {grasas}g fat")
    print(f"Result: {resultado_macros[0]:.1f}% protein | {resultado_macros[1]:.1f}% carbs | {resultado_macros[2]:.1f}% fat")
    assert abs(sum(resultado_macros) - 100) < 0.01, "Percentages should sum to 100!"
    print("✓ Percentages sum to 100\n")

    # --- Mock food database for testing ---
    comida_bd_mock = [
        {"nombre": "Arroz blanco",   "grupo": "AC", "calorias": 350, "proteinas": 7,  "carbohidratos": 77, "grasas": 1},
        {"nombre": "Leche entera",   "grupo": "BA", "calorias": 65,  "proteinas": 3,  "carbohidratos": 5,  "grasas": 4},
        {"nombre": "Zumo de naranja","grupo": "FE", "calorias": 45,  "proteinas": 1,  "carbohidratos": 10, "grasas": 0},
        {"nombre": "Manzana",        "grupo": "FA", "calorias": 52,  "proteinas": 0,  "carbohidratos": 14, "grasas": 0},
        {"nombre": "Huevo cocido",   "grupo": "C",  "calorias": 155, "proteinas": 13, "carbohidratos": 1,  "grasas": 11},
        {"nombre": "Cerveza",        "grupo": "Q",  "calorias": 43,  "proteinas": 0,  "carbohidratos": 4,  "grasas": 0},
        {"nombre": "Chocolate",      "grupo": "S",  "calorias": 500, "proteinas": 5,  "carbohidratos": 60, "grasas": 28},
        {"nombre": "Pan de molde",   "grupo": "AF", "calorias": 265, "proteinas": 9,  "carbohidratos": 49, "grasas": 4},
    ]

    # --- Test filtrar_comida ---
    print("=== filtrar_comida ===")

    resultado_desayuno = filtrar_comida(comida_bd_mock, "desayuno", edad=25)
    print(f"Desayuno indices:        {resultado_desayuno}")
    print(f"  -> {[comida_bd_mock[i]['nombre'] for i in resultado_desayuno]}")

    resultado_bebidas_menor = filtrar_comida(comida_bd_mock, "bebidas", edad=16)
    print(f"Bebidas (age 16) indices: {resultado_bebidas_menor}")
    print(f"  -> {[comida_bd_mock[i]['nombre'] for i in resultado_bebidas_menor]}")

    resultado_bebidas_adulto = filtrar_comida(comida_bd_mock, "bebidas", edad=20)
    print(f"Bebidas (age 20) indices: {resultado_bebidas_adulto}")
    print(f"  -> {[comida_bd_mock[i]['nombre'] for i in resultado_bebidas_adulto]}")

    assert 5 not in resultado_bebidas_menor, "Alcohol should NOT appear for under-18!"
    assert 5 in resultado_bebidas_adulto,    "Alcohol SHOULD appear for 18+!"
    print("✓ Age filter works correctly\n")

    # --- Test traducir_solucion ---
    print("=== traducir_solucion ===")
    # A flat list of food indices — one per food slot across the whole week
    total_slots = sum(c["num_alimentos"] for c in COMIDAS) * len(DIAS_SEMANA)
    solucion_mock = [i % len(comida_bd_mock) for i in range(total_slots)]

    menu, datos_dia = traducir_solucion(solucion_mock, comida_bd_mock)

    for dia, comidas in menu.items():
        print(f"\n{dia}:")
        for nombre_comida, (alimentos, calorias) in comidas.items():
            print(f"  {nombre_comida} ({calorias} kcal):")
            for a in alimentos:
                print(f"    {a}")
        d = datos_dia[dia]
        print(f"  Daily total: {d['calorias']} kcal | "
              f"{d['porcentaje_proteinas']:.1f}% prot | "
              f"{d['porcentaje_carbohidratos']:.1f}% carbs | "
              f"{d['porcentaje_grasas']:.1f}% fat")

    print("\n✓ traducir_solucion ran successfully")