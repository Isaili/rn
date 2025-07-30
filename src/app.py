from flask import Flask, request, jsonify
from flask_cors import CORS
from genetico import algoritmo_genetico
import json
import os
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
CORS(app, resources={r"/optimize": {"origins": "http://127.0.0.1:5500"}})

def generar_reporte_individuo(mejor_individuo, catalogo, area_total, presupuesto_total):
    reporte = {"cultivos": [], "resumen": {}}
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

        reporte["cultivos"].append({
            "nombre": planta['nombre'].capitalize(),
            "cantidad": cantidad,
            "area_ocupada": espacio,
            "produccion": prod,
            "fertilizante": {"unidades": fert, "costo": fert_cost},
            "trabajadores": {"unidades": trab, "costo": trab_cost},
            "ganancia": ingreso
        })

    tiempo_promedio = total_tiempo / total_plantas if total_plantas > 0 else 0
    ganancia_neta = total_ganancia - total_fertilizante_costo - total_trabajo_costo
    produccion_m2 = total_produccion / area_total if area_total > 0 else 0

    reporte["resumen"] = {
        "area_ocupada": total_area,
        "fertilizante_costo": total_fertilizante_costo,
        "trabajo_costo": total_trabajo_costo,
        "trabajadores": total_trabajadores,
        "produccion_total": total_produccion,
        "ganancia_bruta": total_ganancia,
        "ganancia_neta": ganancia_neta,
        "tiempo_promedio": tiempo_promedio,
        "produccion_m2": produccion_m2,
        "tipos_utilizados": tipos_utilizados,
        "presupuesto_utilizado": total_fertilizante_costo + total_trabajo_costo,
        "area_total": area_total,
        "presupuesto_total": presupuesto_total
    }
    return reporte

@app.route('/optimize', methods=['POST'])
def optimize():
    data = request.get_json()
    area_total = data['area']
    presupuesto_total = data['budget']
    
    json_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'catalogo_semillas.json')
    absolute_path = os.path.abspath(json_path)
    print(f"Buscando archivo en: {absolute_path}")
    with open(json_path, 'r', encoding='utf-8') as f:
        catalogo = json.load(f)
    
    mejor, fitness, historial = algoritmo_genetico(
        catalogo=catalogo,
        area_total=area_total,
        presupuesto_total=presupuesto_total,
        generaciones=300,
        tam_poblacion=100,
        tasa_mutacion=0.2,
        elitismo=True
    )
    
    from evaluacion import evaluar_individuo
    evaluacion = evaluar_individuo(mejor, catalogo, area_total, presupuesto_total)
    
    reporte = generar_reporte_individuo(mejor, catalogo, area_total, presupuesto_total)
    
    # Generar gráfico de evolución del fitness
    plt.figure(figsize=(10, 5))
    plt.plot(historial, marker='o', color='green')
    plt.title("Evolución del Fitness por Generación")
    plt.xlabel("Generación")
    plt.ylabel("Fitness del Mejor Individuo")
    plt.grid(True)
    plt.tight_layout()
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_data = base64.b64encode(img.getvalue()).decode('utf-8')
    plt.close()
    
    return jsonify({
        'success': True,
        'reporte': reporte,
        'grafico': plot_data
    })

if __name__ == '__main__':
    app.run(debug=True)