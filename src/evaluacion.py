def evaluar_individuo(individuo, catalogo, area_total, presupuesto_total, trabajadores_max):
    area_ocupada = 0
    suma_tiempo = 0
    total_cantidad = 0
    ganancia_bruta = 0
    costo_total_fertilizante = 0
    costo_total_trabajo = 0
    produccion_total = 0
    trabajadores_utilizados = 0

    for i, cantidad in enumerate(individuo):
        if cantidad == 0:
            continue
        planta = catalogo[i]

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

    # Calcular excesos
    exceso_area = max(0, area_ocupada - area_total)
    exceso_presupuesto = max(0, (costo_total_fertilizante + costo_total_trabajo) - presupuesto_total)
    exceso_trabajadores = max(0, trabajadores_utilizados - trabajadores_max)

    # Penalización por exceder límites
    if exceso_area > 0 or exceso_presupuesto > 0 or exceso_trabajadores > 0:
        return {
            'ganancia_neta': -float('inf'),
            'uso_terreno': 0,
            'tiempo_promedio': float('inf'),
            'costo_fertilizante': costo_total_fertilizante,
            'costo_trabajo': costo_total_trabajo,
            'produccion_por_m2': 0,
            'tipos_cultivo': 0,
            'valido': False
        }

    tiempo_promedio = suma_tiempo / total_cantidad if total_cantidad > 0 else 0
    ganancia_neta = ganancia_bruta - costo_total_fertilizante - costo_total_trabajo
    produccion_por_m2 = produccion_total / area_total if area_total > 0 else 0
    uso_terreno = area_ocupada / area_total if area_total > 0 else 0

    return {
        'ganancia_neta': ganancia_neta,
        'uso_terreno': uso_terreno,
        'tiempo_promedio': tiempo_promedio,
        'costo_fertilizante': costo_total_fertilizante,
        'costo_trabajo': costo_total_trabajo,
        'produccion_por_m2': produccion_por_m2,
        'tipos_cultivo': sum(1 for x in individuo if x > 0),
        'valido': True
    }

def evaluar_poblacion(poblacion, catalogo, area_total, presupuesto_total, trabajadores_max):
    evaluaciones = [evaluar_individuo(ind, catalogo, area_total, presupuesto_total, trabajadores_max) 
                   for ind in poblacion]
    
    # Solo considerar individuos válidos
    evaluaciones_validas = [e for e in evaluaciones if e['valido']]
    
    if not evaluaciones_validas:
        return [0]*len(poblacion), evaluaciones
    
    # Normalización para objetivos
    ganancias = [e['ganancia_neta'] for e in evaluaciones_validas]
    producciones = [e['produccion_por_m2'] for e in evaluaciones_validas]
    tiempos = [e['tiempo_promedio'] for e in evaluaciones_validas]
    
    ganancia_max = max(ganancias)
    produccion_max = max(producciones)
    tiempo_min = min(tiempos)
    
    fitnesses = []
    for e in evaluaciones:
        if not e['valido']:
            fitnesses.append(0)  # Penalización total
            continue
            
        # Ponderación de objetivos
        obj_ganancia = e['ganancia_neta'] / ganancia_max if ganancia_max > 0 else 0
        obj_produccion = e['produccion_por_m2'] / produccion_max if produccion_max > 0 else 0
        obj_tiempo = 1 - (e['tiempo_promedio'] - tiempo_min)/max(tiempo_min, 1) if tiempo_min > 0 else 1
        obj_terreno = e['uso_terreno']
        
        # Fitness ponderado (ajusta los pesos según prioridades)
        fitness = (0.4 * obj_ganancia + 0.3 * obj_produccion + 0.2 * obj_terreno + 0.1 * obj_tiempo)
        fitnesses.append(fitness)
    
    return fitnesses, evaluaciones