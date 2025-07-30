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
    except ValueError:
        print("❌ Error: Entrada inválida. Asegúrate de ingresar valores numéricos.")
        return
    
    print(f"\n🌱 Iniciando optimización con:")
    print(f"   - Terreno: {area_total} m²")
    print(f"   - Presupuesto: ${presupuesto_total:,.2f}")
    print(f"   - Tipos de cultivos disponibles: {len(catalogo_semillas)}")
    
    # Configuración del algoritmo
    generaciones = 300
    tam_poblacion = 100
    tasa_mutacion = 0.2
    elitismo = True
    
    print(f"\n🔬 Configuración del algoritmo:")
    print(f"   - Generaciones: {generaciones}")
    print(f"   - Tamaño población: {tam_poblacion}")
    print(f"   - Tasa mutación: {tasa_mutacion}")
    print(f"   - Elitismo: {'Activado' if elitismo else 'Desactivado'}")
    print(f"\n🚀 Ejecutando algoritmo genético...\n")
    
    # Ejecutar algoritmo genético
    mejor, fitness, historial = algoritmo_genetico(
        catalogo=catalogo_semillas,
        area_total=area_total,
        presupuesto_total=presupuesto_total,
        generaciones=generaciones,
        tam_poblacion=tam_poblacion,
        tasa_mutacion=tasa_mutacion,
        elitismo=elitismo
    )
    
    print(f"\n✅ Optimización completada!")
    print(f"🏆 Fitness final: {fitness:.4f}")
    
    # Reportes
    generar_reporte_individuo(mejor, catalogo_semillas, area_total, presupuesto_total)
    graficar_evolucion_fitness(historial)

if __name__ == "__main__":
    main()