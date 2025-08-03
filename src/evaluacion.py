import numpy as np

def evaluar_individuo(individuo, catalogo, area_total, presupuesto_total):
    """Evalúa un individuo y devuelve métricas detalladas"""
    area_ocupada = 0
    suma_tiempo = 0
    total_cantidad = 0
    ganancia_bruta = 0
    costo_total_fertilizante = 0
    costo_total_trabajo = 0
    produccion_total = 0
    trabajadores_utilizados = 0
    tipos_cultivo = 0
    max_dominancia = 0

    for i, cantidad in enumerate(individuo):
        if cantidad == 0:
            continue
        planta = catalogo[i]
        tipos_cultivo += 1

        espacio_total = planta['espacio'] * cantidad
        tiempo_total = planta['tiempo'] * cantidad
        produccion = planta['rendimiento'] * cantidad
        ingreso = produccion * planta['ganancia_unitaria']
        costo_fertilizante = planta['fertilizante_por_planta'] * cantidad * planta['costo_fertilizante_unitario']
        costo_trabajo = planta['trabajadores_requeridos_por_planta'] * cantidad * planta['costo_trabajador_unitario']
        trabajadores = planta['trabajadores_requeridos_por_planta'] * cantidad

        area_ocupada += espacio_total
        suma_tiempo += tiempo_total
        total_cantidad += cantidad
        ganancia_bruta += ingreso
        costo_total_fertilizante += costo_fertilizante
        costo_total_trabajo += costo_trabajo
        produccion_total += produccion
        trabajadores_utilizados += trabajadores

        # Calcular dominancia de esta planta
        if area_total > 0:
            dominancia = espacio_total / area_total
            max_dominancia = max(max_dominancia, dominancia)

    # Verificar restricciones
    exceso_area = max(0, area_ocupada - area_total)
    exceso_presupuesto = max(0, (costo_total_fertilizante + costo_total_trabajo) - presupuesto_total)

    # Si viola restricciones, aplicar penalización
    if exceso_area > 0 or exceso_presupuesto > 0:
        penalizacion_area = (exceso_area / area_total) * 100 if area_total > 0 else 0
        penalizacion_presupuesto = (exceso_presupuesto / presupuesto_total) * 100 if presupuesto_total > 0 else 0
        penalizacion_total = penalizacion_area + penalizacion_presupuesto
        ganancia_neta = -(1000 + penalizacion_total * 1000)

        return {
            'ganancia_neta': ganancia_neta,
            'uso_terreno': area_ocupada / area_total if area_total > 0 else 0,
            'tiempo_promedio': suma_tiempo / total_cantidad if total_cantidad > 0 else 0,
            'costo_fertilizante': costo_total_fertilizante,
            'costo_trabajo': costo_total_trabajo,
            'produccion_por_m2': 0,
            'produccion_total': produccion_total,
            'tipos_cultivo': tipos_cultivo,
            'trabajadores_requeridos': trabajadores_utilizados,
            'valido': False,
            'penalizacion': penalizacion_total
        }

    # Individuo válido
    tiempo_promedio = suma_tiempo / total_cantidad if total_cantidad > 0 else 0
    ganancia_neta = ganancia_bruta - costo_total_fertilizante - costo_total_trabajo
    produccion_por_m2 = produccion_total / area_total if area_total > 0 else 0
    uso_terreno = area_ocupada / area_total if area_total > 0 else 0

    # Penalización por dominancia excesiva (umbral 0.6)
    penalizacion_dominancia = max(0, (max_dominancia - 0.6) * 100) if max_dominancia > 0.6 else 0

    # Penalización por uso excesivo de trabajadores
    max_trabajadores_esperados = area_total * 0.3 / 0.2
    penalizacion_trabajadores = max(0, (trabajadores_utilizados - max_trabajadores_esperados) / max_trabajadores_esperados) * 10 if max_trabajadores_esperados > 0 else 0

    return {
        'ganancia_neta': ganancia_neta,
        'uso_terreno': uso_terreno,
        'tiempo_promedio': tiempo_promedio,
        'costo_fertilizante': costo_total_fertilizante,
        'costo_trabajo': costo_total_trabajo,
        'produccion_por_m2': produccion_por_m2,
        'produccion_total': produccion_total,
        'tipos_cultivo': tipos_cultivo,
        'trabajadores_requeridos': trabajadores_utilizados,
        'valido': True,
        'penalizacion': penalizacion_dominancia + penalizacion_trabajadores
    }

def evaluar_poblacion(poblacion, catalogo, area_total, presupuesto_total):
    """Evalúa toda la población y calcula fitness normalizado con múltiples objetivos"""
    evaluaciones = [evaluar_individuo(ind, catalogo, area_total, presupuesto_total)
                   for ind in poblacion]

    # Separar individuos válidos e inválidos
    evaluaciones_validas = [e for e in evaluaciones if e['valido']]
    evaluaciones_invalidas = [e for e in evaluaciones if not e['valido']]

    fitnesses = []

    # Si no hay individuos válidos, asignar fitness muy bajo a todos
    if not evaluaciones_validas:
        for e in evaluaciones:
            if e['valido']:
                fitnesses.append(0.1)
            else:
                fitness_invalido = max(-1.0, -0.1 - (e['penalizacion'] / 100))
                fitnesses.append(fitness_invalido)
        return fitnesses, evaluaciones

    # Calcular rangos para normalización SOLO con individuos válidos
    ganancias_validas = [e['ganancia_neta'] for e in evaluaciones_validas]
    producciones_validas = [e['produccion_total'] for e in evaluaciones_validas]  # Maximizar producción total
    usos_terreno_validos = [e['uso_terreno'] for e in evaluaciones_validas]      # Maximizar aprovechamiento
    tiempos_validos = [e['tiempo_promedio'] for e in evaluaciones_validas if e['tiempo_promedio'] > 0]  # Minimizar tiempo
    trabajadores_validos = [e['trabajadores_requeridos'] for e in evaluaciones_validas]

    # Valores para normalización
    ganancia_max = max(ganancias_validas) if ganancias_validas else 1
    ganancia_min = min(ganancias_validas) if ganancias_validas else 0
    produccion_max = max(producciones_validas) if producciones_validas else 1
    uso_terreno_max = max(usos_terreno_validos) if usos_terreno_validos else 1
    tiempo_max = max(tiempos_validos) if tiempos_validos else 1
    tiempo_min = min(tiempos_validos) if tiempos_validos else 0
    trabajadores_min = min(trabajadores_validos) if trabajadores_validos else 0
    trabajadores_max = max(trabajadores_validos) if trabajadores_validos else 1

    # Evitar divisiones por cero
    ganancia_rango = max(ganancia_max - ganancia_min, 1)
    produccion_rango = max(produccion_max, 1)
    tiempo_rango = max(tiempo_max - tiempo_min, 1)
    trabajadores_rango = max(trabajadores_max - trabajadores_min, 1)

    # Calcular fitness para cada individuo
    for e in evaluaciones:
        if not e['valido']:
            fitness_invalido = max(-1.0, -0.1 - (e['penalizacion'] / 100))
            fitnesses.append(fitness_invalido)
            continue

        # Normalizar objetivos para individuos válidos
        obj_ganancia = (e['ganancia_neta'] - ganancia_min) / ganancia_rango if ganancia_rango > 0 else 0  # Maximizar ganancias
        obj_produccion = e['produccion_total'] / produccion_max if produccion_max > 0 else 0  # Maximizar producción
        obj_terreno = e['uso_terreno'] / uso_terreno_max if uso_terreno_max > 0 else 0  # Maximizar aprovechamiento
        if tiempo_rango > 0 and e['tiempo_promedio'] > 0:
            obj_tiempo = 1 - ((e['tiempo_promedio'] - tiempo_min) / tiempo_rango)  # Minimizar tiempo
        else:
            obj_tiempo = 1
        obj_trabajadores = 1 - ((e['trabajadores_requeridos'] - trabajadores_min) / trabajadores_rango) if trabajadores_rango > 0 else 1  # Minimizar trabajadores (opcional)

        # Bonus por diversificación
        bonus_diversidad = min(e['tipos_cultivo'] * 0.2 / 20, 0.2) if 20 > 0 else 0  # Máximo 20 tipos como referencia

        # Penalización por dominancia excesiva
        penalizacion_dominancia = e['penalizacion'] * 0.1

        # Fitness ponderado con los cuatro objetivos
        fitness = (0.25 * obj_ganancia +    # Maximizar ganancias
                   0.25 * obj_produccion +  # Maximizar producción
                   0.25 * obj_terreno +     # Maximizar aprovechamiento del terreno
                   0.25 * obj_tiempo +      # Minimizar tiempo de producción
                   bonus_diversidad -
                   penalizacion_dominancia)

        # Asegurar que el fitness esté en rango [0.1, 1.0] para individuos válidos
        fitness = max(0.1, min(1.0, fitness))
        fitnesses.append(fitness)

    return fitnesses, evaluaciones