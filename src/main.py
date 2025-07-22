import json
import os
from genetico import algoritmo_genetico
from reporte import generar_reporte_individuo, graficar_evolucion_fitness

def main():
    print("=== AGROGEN: Optimización de Cultivos con Algoritmos Genéticos ===")

    # Ruta al JSON
    ruta_json = os.path.join(os.path.dirname(__file__), "..", "data", "catalogo_semillas.json")

    if not os.path.exists(ruta_json):
        print("❌ Error: No se encontró el archivo 'catalogo_semillas.json'")
        return

    # Cargar el catálogo
    with open(ruta_json, "r", encoding="utf-8") as f:
        try:
            catalogo_semillas = json.load(f)
        except json.JSONDecodeError:
            print("❌ Error: El archivo JSON no tiene un formato válido.")
            return

    if not isinstance(catalogo_semillas, list) or len(catalogo_semillas) < 2:
        print("❌ Error: El catálogo debe contener al menos 2 tipos de semillas.")
        return

    # Entradas del usuario
    try:
        area_total = float(input("Ingresa área total del terreno (m²): "))
        presupuesto_total = float(input("Ingresa presupuesto total disponible: "))
        trabajadores_max = int(input("Número máximo de trabajadores disponibles: "))
    except ValueError:
        print("❌ Error: Entrada inválida. Asegúrate de ingresar valores numéricos.")
        return

    # Configuración del algoritmo
    generaciones = 100
    tam_poblacion = 30
    tasa_mutacion = 0.1
    elitismo = True

    # Ejecutar algoritmo genético
    mejor, fitness, historial = algoritmo_genetico(
        catalogo=catalogo_semillas,
        area_total=area_total,
        presupuesto_total=presupuesto_total,
        trabajadores_max=trabajadores_max,
        generaciones=generaciones,
        tam_poblacion=tam_poblacion,
        tasa_mutacion=tasa_mutacion,
        elitismo=elitismo
    )

    # Reportes
    generar_reporte_individuo(mejor, catalogo_semillas, area_total, presupuesto_total, trabajadores_max)
    graficar_evolucion_fitness(historial)

if __name__ == "__main__":
    main()