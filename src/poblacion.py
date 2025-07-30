import random

def calcular_rentabilidad(planta):
    """Calcula la rentabilidad por unidad de espacio y tiempo"""
    costo_total = (planta['fertilizante_por_planta'] * planta['costo_fertilizante_unitario'] +
                   planta['trabajadores_requeridos_por_planta'] * planta['costo_trabajador_unitario'])
    ganancia_neta = (planta['rendimiento'] * planta['ganancia_unitaria']) - costo_total
    
    rentabilidad_espacial = ganancia_neta / planta['espacio'] if planta['espacio'] > 0 else 0
    rentabilidad_temporal = ganancia_neta / planta['tiempo'] if planta['tiempo'] > 0 else 0
    
    return rentabilidad_espacial * 0.7 + rentabilidad_temporal * 0.3

def generar_poblacion_inicial(catalogo, area_total, presupuesto_total, tam_poblacion):
    """Genera población inicial con diversas estrategias"""
    poblacion = []
    
    plantas_con_indice = [(i, planta, calcular_rentabilidad(planta)) 
                         for i, planta in enumerate(catalogo)]
    plantas_ordenadas = sorted(plantas_con_indice, key=lambda x: x[2], reverse=True)
    
    for _ in range(tam_poblacion):
        individuo = [0] * len(catalogo)
        estrategia = random.choice(['greedy', 'diversificada', 'aleatoria', 'balanceada'])
        
        if estrategia == 'greedy':
            area_usada = 0
            costo_usado = 0
            
            for i, planta, rentabilidad in plantas_ordenadas:
                if rentabilidad <= 0:
                    continue
                    
                max_por_area = int((area_total - area_usada) // planta['espacio']) if planta['espacio'] > 0 else 0
                
                costo_unitario = (planta['fertilizante_por_planta'] * planta['costo_fertilizante_unitario'] +
                                planta['trabajadores_requeridos_por_planta'] * planta['costo_trabajador_unitario'])
                max_por_presupuesto = int((presupuesto_total - costo_usado) / costo_unitario) if costo_unitario > 0 else 0
                
                max_posible = max(0, min(max_por_area, max_por_presupuesto))
                
                if max_posible > 0:
                    cantidad = random.randint(int(max_posible * 0.7), max_posible)
                    individuo[i] = cantidad
                    
                    area_usada += cantidad * planta['espacio']
                    costo_usado += cantidad * costo_unitario
        
        elif estrategia == 'diversificada':
            area_usada = 0
            costo_usado = 0
            
            plantas_mezcladas = plantas_ordenadas.copy()
            random.shuffle(plantas_mezcladas)
            
            for i, planta, rentabilidad in plantas_mezcladas:
                if rentabilidad <= 0:
                    continue
                
                max_por_area = int((area_total - area_usada) // planta['espacio']) if planta['espacio'] > 0 else 0
                
                costo_unitario = (planta['fertilizante_por_planta'] * planta['costo_fertilizante_unitario'] +
                                planta['trabajadores_requeridos_por_planta'] * planta['costo_trabajador_unitario'])
                max_por_presupuesto = int((presupuesto_total - costo_usado) / costo_unitario) if costo_unitario > 0 else 0
                
                max_posible = max(0, min(max_por_area, max_por_presupuesto))
                
                if max_posible > 0:
                    cantidad = random.randint(1, min(max_posible, max(1, int(max_posible * 0.3))))
                    individuo[i] = cantidad
                    
                    area_usada += cantidad * planta['espacio']
                    costo_usado += cantidad * costo_unitario
        
        elif estrategia == 'balanceada':
            area_usada = 0
            costo_usado = 0
            
            plantas_top = plantas_ordenadas[:len(plantas_ordenadas)//2]
            random.shuffle(plantas_top)
            
            for i, planta, rentabilidad in plantas_top:
                if rentabilidad <= 0:
                    continue
                
                max_por_area = int((area_total - area_usada) // planta['espacio']) if planta['espacio'] > 0 else 0
                
                costo_unitario = (planta['fertilizante_por_planta'] * planta['costo_fertilizante_unitario'] +
                                planta['trabajadores_requeridos_por_planta'] * planta['costo_trabajador_unitario'])
                max_por_presupuesto = int((presupuesto_total - costo_usado) / costo_unitario) if costo_unitario > 0 else 0
                
                max_posible = max(0, min(max_por_area, max_por_presupuesto))
                
                if max_posible > 0:
                    cantidad = random.randint(int(max_posible * 0.4), int(max_posible * 0.8))
                    if cantidad > 0:
                        individuo[i] = cantidad
                        
                        area_usada += cantidad * planta['espacio']
                        costo_usado += cantidad * costo_unitario
        
        else:
            area_usada = 0
            costo_usado = 0
            
            indices_disponibles = list(range(len(catalogo)))
            random.shuffle(indices_disponibles)
            
            for i in indices_disponibles:
                planta = catalogo[i]
                
                if random.random() < 0.5:
                    continue
                
                max_por_area = int((area_total - area_usada) // planta['espacio']) if planta['espacio'] > 0 else 0
                
                costo_unitario = (planta['fertilizante_por_planta'] * planta['costo_fertilizante_unitario'] +
                                planta['trabajadores_requeridos_por_planta'] * planta['costo_trabajador_unitario'])
                max_por_presupuesto = int((presupuesto_total - costo_usado) / costo_unitario) if costo_unitario > 0 else 0
                
                max_posible = max(0, min(max_por_area, max_por_presupuesto))
                
                if max_posible > 0:
                    cantidad = random.randint(1, max_posible)
                    individuo[i] = cantidad
                    
                    area_usada += cantidad * planta['espacio']
                    costo_usado += cantidad * costo_unitario
        
        poblacion.append(individuo)
    
    return poblacion