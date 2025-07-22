import random
import numpy as np
from evaluacion import evaluar_poblacion

def seleccion_por_ruleta(poblacion, fitnesses):
    total_fitness = sum(fitnesses)
    if total_fitness == 0:
        return random.choices(poblacion, k=len(poblacion))
    probabilidades = [f/total_fitness for f in fitnesses]
    return random.choices(poblacion, weights=probabilidades, k=len(poblacion))

def seleccion_por_torneo(poblacion, fitnesses, k=3):
    seleccionados = []
    for _ in range(len(poblacion)):
        participantes = random.sample(list(zip(poblacion, fitnesses)), k)
        ganador = max(participantes, key=lambda x: x[1])
        seleccionados.append(ganador[0])
    return seleccionados

def emparejamiento_por_aptitud(poblacion, fitnesses):
    # Emparejar individuos con fitness similar
    parejas = []
    indices = np.argsort(fitnesses)
    mitad = len(indices) // 2
    for i in range(mitad):
        parejas.append((poblacion[indices[i]], poblacion[indices[mitad+i]]))
    return parejas

def cruza_uniforme(padre1, padre2):
    hijo1 = []
    hijo2 = []
    for gen1, gen2 in zip(padre1, padre2):
        if random.random() < 0.5:
            hijo1.append(gen1)
            hijo2.append(gen2)
        else:
            hijo1.append(gen2)
            hijo2.append(gen1)
    return hijo1, hijo2

def cruza_por_puntos(padre1, padre2, n_puntos=2):
    puntos = sorted(random.sample(range(1, len(padre1)), n_puntos))
    hijo1 = []
    hijo2 = []
    prev = 0
    for punto in puntos + [len(padre1)]:
        hijo1.extend(padre1[prev:punto])
        hijo2.extend(padre2[prev:punto])
        padre1, padre2 = padre2, padre1  # Alternamos los padres
        prev = punto
    return hijo1, hijo2

def mutacion_gaussiana(individuo, catalogo, sigma=0.1):
    nuevo = individuo.copy()
    for i in range(len(nuevo)):
        if random.random() < 0.1:  # Probabilidad de mutación
            cambio = int(round(random.gauss(0, sigma) * nuevo[i]))
            nuevo[i] = max(0, nuevo[i] + cambio)
    return nuevo

def mutacion_aleatoria(individuo, catalogo, area_total, presupuesto_total, trabajadores_max):
    nuevo = individuo.copy()
    i = random.randint(0, len(nuevo)-1)
    planta = catalogo[i]
    
    max_posible = min(
        int(area_total // planta['espacio']),
        int(presupuesto_total // (planta['fertilizante_por_planta'] * planta['costo_fertilizante_unitario'] + 
                               planta['trabajadores_requeridos_por_planta'] * planta['costo_trabajador_unitario'])),
        int(trabajadores_max // planta['trabajadores_requeridos_por_planta'])
    )
    
    if max_posible > 0:
        nuevo[i] = random.randint(0, max_posible)
    return nuevo

def poda_por_umbral(poblacion, fitnesses, umbral=0.5):
    promedio = sum(fitnesses) / len(fitnesses)
    nueva_poblacion = []
    for ind, fit in zip(poblacion, fitnesses):
        if fit >= umbral * promedio or random.random() < 0.1:  # 10% de probabilidad de mantener algunos malos
            nueva_poblacion.append(ind)
    # Completar con nuevos individuos si es necesario
    while len(nueva_poblacion) < len(poblacion):
        nueva_poblacion.append([random.randint(0, 10) for _ in range(len(poblacion[0]))])
    return nueva_poblacion[:len(poblacion)]

def nueva_generacion(poblacion, fitnesses, catalogo, area_total, presupuesto_total, trabajadores_max, 
                    elitismo=True, tasa_mutacion=0.2, metodo_seleccion='torneo'):
    nueva_poblacion = []

    # Elitismo: conservar el mejor individuo
    if elitismo:
        mejor_ind = max(zip(poblacion, fitnesses), key=lambda x: x[1])
        nueva_poblacion.append(mejor_ind[0])

    # Selección
    if metodo_seleccion == 'ruleta':
        seleccionados = seleccion_por_ruleta(poblacion, fitnesses)
    else:  # torneo por defecto
        seleccionados = seleccion_por_torneo(poblacion, fitnesses)

    # Emparejamiento y cruza
    parejas = emparejamiento_por_aptitud(seleccionados, fitnesses)
    for padre1, padre2 in parejas:
        if random.random() < 0.7:  # Probabilidad de cruza
            if random.random() < 0.5:
                hijo1, hijo2 = cruza_uniforme(padre1, padre2)
            else:
                hijo1, hijo2 = cruza_por_puntos(padre1, padre2)
            nueva_poblacion.extend([hijo1, hijo2])
        else:
            nueva_poblacion.extend([padre1.copy(), padre2.copy()])

    # Mutación
    for i in range(len(nueva_poblacion)):
        if random.random() < tasa_mutacion:
            if random.random() < 0.5:
                nueva_poblacion[i] = mutacion_gaussiana(nueva_poblacion[i], catalogo)
            else:
                nueva_poblacion[i] = mutacion_aleatoria(nueva_poblacion[i], catalogo, 
                                                      area_total, presupuesto_total, trabajadores_max)

    # Poda
    if len(nueva_poblacion) > len(poblacion):
        fitnesses_nuevos, _ = evaluar_poblacion(nueva_poblacion, catalogo, area_total, presupuesto_total, trabajadores_max)
        nueva_poblacion = poda_por_umbral(nueva_poblacion, fitnesses_nuevos)

    return nueva_poblacion[:len(poblacion)]

def algoritmo_genetico(catalogo, area_total, presupuesto_total, trabajadores_max,
                     generaciones=100, tam_poblacion=50, tasa_mutacion=0.2, elitismo=True):
    
    from poblacion import generar_poblacion_inicial
    
    poblacion = generar_poblacion_inicial(catalogo, area_total, presupuesto_total, trabajadores_max, tam_poblacion)
    mejor_fitness_por_generacion = []
    mejor_individuo_global = None
    mejor_fitness_global = -float('inf')
    
    for gen in range(generaciones):
        fitnesses, evaluaciones = evaluar_poblacion(poblacion, catalogo, area_total, presupuesto_total, trabajadores_max)
        
        idx_mejor = np.argmax(fitnesses)
        if fitnesses[idx_mejor] > mejor_fitness_global:
            mejor_fitness_global = fitnesses[idx_mejor]
            mejor_individuo_global = poblacion[idx_mejor]
        
        mejor_fitness_por_generacion.append(fitnesses[idx_mejor])
        print(f"Generación {gen+1} | Mejor fitness: {fitnesses[idx_mejor]:.4f} | Uso terreno: {evaluaciones[idx_mejor]['uso_terreno']:.2%}")
        
        # Variar la tasa de mutación para evitar estancamiento
        tasa_actual = tasa_mutacion * (1 + 0.5 * np.sin(gen/10))
        poblacion = nueva_generacion(poblacion, fitnesses, catalogo, area_total, presupuesto_total, 
                                   trabajadores_max, elitismo, tasa_actual)
    
    return mejor_individuo_global, mejor_fitness_global, mejor_fitness_por_generacion