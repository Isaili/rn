import random

def generar_poblacion_inicial(catalogo, area_total, presupuesto_total, trabajadores_max, tam_poblacion):
    poblacion = []
    
    for _ in range(tam_poblacion):
        individuo = [0]*len(catalogo)
        area_usada = 0
        costo_usado = 0
        trabajadores_usados = 0
        
        # Ordenar plantas por rentabilidad (ganancia/espacio)
        plantas_ordenadas = sorted(
            [(i, p) for i, p in enumerate(catalogo)],
            key=lambda x: (x[1]['ganancia_unitaria']/x[1]['espacio'], -x[1]['tiempo']),
            reverse=True
        )
        
        for i, planta in plantas_ordenadas:
            max_posible = min(
                int((area_total - area_usada) // planta['espacio']),
                int((presupuesto_total - costo_usado) / (
                    planta['fertilizante_por_planta']*planta['costo_fertilizante_unitario'] +
                    planta['trabajadores_requeridos_por_planta']*planta['costo_trabajador_unitario']
                )) if (planta['fertilizante_por_planta']*planta['costo_fertilizante_unitario'] +
                      planta['trabajadores_requeridos_por_planta']*planta['costo_trabajador_unitario']) > 0 else float('inf'),
                int((trabajadores_max - trabajadores_usados) / planta['trabajadores_requeridos_por_planta']) 
                if planta['trabajadores_requeridos_por_planta'] > 0 else float('inf')
            )
            
            if max_posible >= 1:
                cantidad = random.randint(0, int(max_posible))
                individuo[i] = cantidad
                area_usada += cantidad * planta['espacio']
                costo_usado += cantidad * (
                    planta['fertilizante_por_planta']*planta['costo_fertilizante_unitario'] +
                    planta['trabajadores_requeridos_por_planta']*planta['costo_trabajador_unitario']
                )
                trabajadores_usados += cantidad * planta['trabajadores_requeridos_por_planta']
        
        poblacion.append(individuo)
    
    return poblacion