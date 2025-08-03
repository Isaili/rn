import matplotlib.pyplot as plt

def generar_reporte_individuo(mejor_individuo, catalogo, area_total, presupuesto_total):
    total_area = 0
    total_fertilizante = 0
    total_fertilizante_costo = 0
    total_trabajadores = 0
    total_trabajo_costo = 0
    total_ganancia = 0
    total_produccion = 0
    total_tiempo = 0
    total_plantas = 0
    tipos_utilizados = 0

    print("\n📊 CONFIGURACIÓN ÓPTIMA DE CULTIVOS:\n")

    for i, cantidad in enumerate(mejor_individuo):
        if cantidad == 0:
            continue

        planta = catalogo[i]
        tipos_utilizados += 1

        espacio = planta['espacio'] * cantidad
        fert = planta['fertilizante_por_planta'] * cantidad
        fert_cost = fert * planta['costo_fertilizante_unitario']
        trab = planta['trabajadores_requeridos_por_planta'] * cantidad
        trab_cost = trab * planta['costo_trabajador_unitario']
        prod = planta['rendimiento'] * cantidad
        ingreso = prod * planta['ganancia_unitaria']
        tiempo = planta['tiempo'] * cantidad

        total_area += espacio
        total_fertilizante += fert
        total_fertilizante_costo += fert_cost
        total_trabajadores += trab
        total_trabajo_costo += trab_cost
        total_ganancia += ingreso
        total_produccion += prod
        total_tiempo += tiempo
        total_plantas += cantidad

        print(f"🌱 {planta['nombre'].capitalize()}:")
        print(f"   - Cantidad a sembrar: {cantidad}")
        print(f"   - Área ocupada: {espacio:.2f} m²")
        print(f"   - Producción estimada: {prod:.2f} unidades")
        print(f"   - Fertilizante necesario: {fert:.2f} unidades (${fert_cost:.2f})")
        print(f"   - Trabajadores necesarios: {trab:.2f} personas (${trab_cost:.2f})")
        print(f"   - Ganancia estimada: ${ingreso:.2f}\n")

    tiempo_promedio = total_tiempo / total_plantas if total_plantas > 0 else 0
    ganancia_neta = total_ganancia - total_fertilizante_costo - total_trabajo_costo
    produccion_m2 = total_produccion / area_total

    print("📈 RESUMEN GENERAL:")
    print(f"- Área total ocupada: {total_area:.2f} m² de {area_total} m² ({(total_area/area_total)*100:.2f}%)")
    print(f"- Costo total en fertilizante: ${total_fertilizante_costo:.2f}")
    print(f"- Costo total en mano de obra: ${total_trabajo_costo:.2f}")
    print(f"- Trabajadores requeridos: {total_trabajadores:.2f}")
    print(f"- Producción total: {total_produccion:.2f} unidades")
    print(f"- Ganancia bruta: ${total_ganancia:.2f}")
    print(f"- Ganancia neta: ${ganancia_neta:.2f}")
    print(f"- Tiempo promedio de cultivo: {tiempo_promedio:.2f} días")
    print(f"- Producción por m²: {produccion_m2:.2f}")
    print(f"- Diversificación: {tipos_utilizados} tipo(s) de planta")
    print(f"- Presupuesto utilizado estimado: ${total_fertilizante_costo + total_trabajo_costo:.2f} de ${presupuesto_total}")

def graficar_evolucion_fitness(fitness_por_generacion):
    plt.figure(figsize=(10, 5))
    plt.plot(fitness_por_generacion, marker='o', color='green')
    plt.title("Evolución del Fitness por Generación")
    plt.xlabel("Generación")
    plt.ylabel("Fitness del Mejor Individuo")
    plt.grid(True)
    plt.tight_layout()
    plt.show()