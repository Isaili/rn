from flask import Flask, request, jsonify
from flask_cors import CORS
from genetico import algoritmo_genetico
import json
import os
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
# Configuración CORS más flexible para desarrollo
CORS(app, resources={r"/optimize": {"origins": "*"}})

def generar_reporte_individuo(mejor_individuo, catalogo, area_total, presupuesto_total):
    """Genera un reporte detallado del mejor individuo encontrado"""
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
    try:
        # Validación de datos de entrada
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No se recibieron datos'}), 400
        
        area_total = float(data.get('area', 0))
        presupuesto_total = float(data.get('budget', 0))
        
        if area_total <= 0 or presupuesto_total <= 0:
            return jsonify({'success': False, 'error': 'Área y presupuesto deben ser mayores a 0'}), 400

        # Carga del catálogo con manejo de errores
        json_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'catalogo_semillas.json')
        absolute_path = os.path.abspath(json_path)
        print(f"Buscando archivo en: {absolute_path}")
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                catalogo = json.load(f)
        except FileNotFoundError:
            return jsonify({'success': False, 'error': f'Archivo no encontrado: {absolute_path}'}), 500
        except json.JSONDecodeError:
            return jsonify({'success': False, 'error': 'Error al decodificar el archivo JSON'}), 500

        # Ejecución del algoritmo genético
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

    except Exception as e:
        app.logger.error(f"Error en /optimize: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)