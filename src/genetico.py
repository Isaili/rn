import random
import numpy as np
from evaluacion import evaluar_poblacion
from poblacion import generar_poblacion_inicial

# =======================
# SELECCIÓN POR TORNEO
# =======================
def seleccion_por_torneo(poblacion, fitnesses, k=3):
    seleccionados = []
    for _ in range(len(poblacion)):
        indices_positivos = [i for i, f in enumerate(fitnesses) if f > 0]
        indices_torneo = random.sample(indices_positivos, k) if len(indices_positivos) >= k else indices_positivos
        if indices_torneo:
            mejor_idx = max(indices_torneo, key=lambda i: fitnesses[i])
            seleccionados.append(poblacion[mejor_idx])
        else:
            seleccionados.append(random.choice(poblacion))
    return seleccionados

# =======================
# CRUZA UNIFORME
# =======================
def cruza_uniforme(padre1, padre2, prob_cruza=0.5):
    hijo1, hijo2 = [], []
    for gen1, gen2 in zip(padre1, padre2):
        if random.random() < prob_cruza:
            hijo1.append(gen2)
            hijo2.append(gen1)
        else:
            hijo1.append(gen1)
            hijo2.append(gen2)
    return hijo1, hijo2

# =======================
# MUTACIÓN CONSERVADORA
# =======================
def mutacion_conservadora(individuo, catalogo, area_total, presupuesto_total, intensidad=0.3):
    nuevo = individuo.copy()
    if random.random() < intensidad:
        gen_mutado = random.randint(0, len(nuevo) - 1)
        area_usada_otros = 0
        costo_usado_otros = 0
        for i, cantidad in enumerate(nuevo):
            if i == gen_mutado or cantidad == 0:
                continue
            planta = catalogo[i]
            area_usada_otros += planta['espacio'] * cantidad
            costo_usado_otros += cantidad * (
                planta['fertilizante_por_planta'] * planta['costo_fertilizante_unitario'] +
                planta['trabajadores_requeridos_por_planta'] * planta['costo_trabajador_unitario']
            )
        planta_mutada = catalogo[gen_mutado]
        area_disponible = area_total - area_usada_otros
        presupuesto_disponible = presupuesto_total - costo_usado_otros
        max_por_area = int(area_disponible // planta_mutada['espacio']) if planta_mutada['espacio'] > 0 else 0
        costo_unitario = (
            planta_mutada['fertilizante_por_planta'] * planta_mutada['costo_fertilizante_unitario'] +
            planta_mutada['trabajadores_requeridos_por_planta'] * planta_mutada['costo_trabajador_unitario']
        )
        max_por_presupuesto = int(presupuesto_disponible // costo_unitario) if costo_unitario > 0 else 0
        max_permitido = max(0, min(max_por_area, max_por_presupuesto))
        nuevo[gen_mutado] = random.randint(0, max_permitido) if max_permitido > 0 else 0
    else:
        genes_no_cero = [i for i, x in enumerate(nuevo) if x > 0]
        if genes_no_cero:
            gen_ajustar = random.choice(genes_no_cero)
            ajuste = random.choice([-1, 1])
            nuevo[gen_ajustar] = max(0, nuevo[gen_ajustar] + ajuste)
    return nuevo

# =======================
# REPARACIÓN SUAVE
# =======================
def reparar_individuo_suave(individuo, catalogo, area_total, presupuesto_total):
    nuevo = individuo.copy()
    max_iteraciones = 50
    iteracion = 0
    while iteracion < max_iteraciones:
        area_usada = sum(catalogo[i]['espacio'] * cantidad for i, cantidad in enumerate(nuevo))
        costo_usado = sum(cantidad * (
            catalogo[i]['fertilizante_por_planta'] * catalogo[i]['costo_fertilizante_unitario'] +
            catalogo[i]['trabajadores_requeridos_por_planta'] * catalogo[i]['costo_trabajador_unitario']
        ) for i, cantidad in enumerate(nuevo))
        if area_usada <= area_total and costo_usado <= presupuesto_total:
            break
        genes_no_cero = [(i, cantidad) for i, cantidad in enumerate(nuevo) if cantidad > 0]
        if not genes_no_cero:
            break
        eficiencias = []
        for i, cantidad in genes_no_cero:
            planta = catalogo[i]
            costo_unitario = (
                planta['fertilizante_por_planta'] * planta['costo_fertilizante_unitario'] +
                planta['trabajadores_requeridos_por_planta'] * planta['costo_trabajador_unitario']
            )
            eficiencia = (planta['rendimiento'] * planta['ganancia_unitaria']) / max(costo_unitario, 1)
            eficiencias.append((i, eficiencia))
        gen_a_reducir = min(eficiencias, key=lambda x: x[1])[0]
        nuevo[gen_a_reducir] = max(0, nuevo[gen_a_reducir] - 1)
        iteracion += 1
    return nuevo

# =======================
# PODA POR DIVERSIDAD
# =======================
def calcular_similitud(ind1, ind2):
    if len(ind1) != len(ind2):
        return 0
    iguales = sum(1 for a, b in zip(ind1, ind2) if a == b)
    return iguales / len(ind1)

def poda_por_diversidad(poblacion, umbral_similitud=0.95):
    poblacion_filtrada = []
    for ind in poblacion:
        es_similar = any(calcular_similitud(ind, otro) >= umbral_similitud for otro in poblacion_filtrada)
        if not es_similar:
            poblacion_filtrada.append(ind)
    while len(poblacion_filtrada) < len(poblacion):
        poblacion_filtrada.append(random.choice(poblacion))
    return poblacion_filtrada

# =======================
# ALGORITMO GENÉTICO
# =======================
def algoritmo_genetico(catalogo, area_total, presupuesto_total,
                      generaciones=100, tam_poblacion=50, tasa_mutacion=0.1, elitismo=True):
    poblacion = generar_poblacion_inicial(catalogo, area_total, presupuesto_total, tam_poblacion)
    poblacion = [reparar_individuo_suave(ind, catalogo, area_total, presupuesto_total) for ind in poblacion]
    
    mejor_fitness_por_generacion = []
    mejor_individuo_global = None
    mejor_fitness_global = -float('inf')
    generaciones_sin_mejora = 0
    elite_size = max(3, int(tam_poblacion * 0.2)) if elitismo else 0

    for gen in range(generaciones):
        fitnesses, evaluaciones = evaluar_poblacion(poblacion, catalogo, area_total, presupuesto_total)
        if fitnesses:
            idx_mejor = np.argmax(fitnesses)
            fitness_actual = fitnesses[idx_mejor]
            if fitness_actual > mejor_fitness_global:
                mejor_fitness_global = fitness_actual
                mejor_individuo_global = poblacion[idx_mejor].copy()
                generaciones_sin_mejora = 0
                print(f"🎯 Nueva mejor solución en generación {gen+1}: {fitness_actual:.4f}")
            else:
                generaciones_sin_mejora += 1
            mejor_fitness_por_generacion.append(mejor_fitness_global)
            individuos_validos = sum(1 for e in evaluaciones if e['valido'])
            print(f"Gen {gen+1:3d} | Mejor Global: {mejor_fitness_global:.4f} | Actual: {fitness_actual:.4f} | Válidos: {individuos_validos}/{len(poblacion)}")
        
        nueva_poblacion = []

        # Elitismo
        if elitismo and fitnesses:
            indices_ordenados = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i], reverse=True)
            for i in range(min(elite_size, len(indices_ordenados))):
                if fitnesses[indices_ordenados[i]] > 0:
                    nueva_poblacion.append(poblacion[indices_ordenados[i]].copy())

        # Reproducción
        while len(nueva_poblacion) < tam_poblacion:
            indices_validos = [i for i, f in enumerate(fitnesses) if f > 0]
            if len(indices_validos) >= 2:
                padres_validos = [poblacion[i] for i in indices_validos]
                fitnesses_validos = [fitnesses[i] for i in indices_validos]
                padres_seleccionados = seleccion_por_torneo(padres_validos, fitnesses_validos, k=3)
                if len(padres_seleccionados) >= 2:
                    padre1, padre2 = random.sample(padres_seleccionados, 2)
                    if random.random() < 0.8:
                        hijo1, hijo2 = cruza_uniforme(padre1, padre2, prob_cruza=0.4)
                    else:
                        hijo1, hijo2 = padre1.copy(), padre2.copy()
                    hijo1 = reparar_individuo_suave(hijo1, catalogo, area_total, presupuesto_total)
                    hijo2 = reparar_individuo_suave(hijo2, catalogo, area_total, presupuesto_total)
                    nueva_poblacion.extend([hijo1, hijo2])
            else:
                nuevos = generar_poblacion_inicial(catalogo, area_total, presupuesto_total, 2)
                nueva_poblacion.extend(nuevos[:2])

        nueva_poblacion = nueva_poblacion[:tam_poblacion]

        # Mutación
        inicio_mutacion = elite_size if elitismo else 0
        for i in range(inicio_mutacion, len(nueva_poblacion)):
            if random.random() < tasa_mutacion:
                nueva_poblacion[i] = mutacion_conservadora(
                    nueva_poblacion[i], catalogo, area_total, presupuesto_total, intensidad=0.2
                )

        # 📌 Poda final por diversidad
        nueva_poblacion = poda_por_diversidad(nueva_poblacion, umbral_similitud=0.95)

        poblacion = nueva_poblacion

        if generaciones_sin_mejora > 30 and gen > 50:
            print(f"Parada temprana en generación {gen+1} por convergencia")
            break

    return mejor_individuo_global, mejor_fitness_global, mejor_fitness_por_generacion
