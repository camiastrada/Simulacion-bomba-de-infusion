from sistema import SistemaInfusionAcoplado
from xdevs.sim import Coordinator
from monitores.monitor_caudal import MonitorCaudal
from monitores.monitor_alarmas import MonitorAlarmas
from monitores.monitor_respuesta import MonitorRespuesta

if __name__ == "__main__":
    # 1. Crear el sistema acoplado (la maqueta completa)
    sistema = SistemaInfusionAcoplado("Suite_Simulacion_Medica")

    # 2. Crear los monitores
    monitor_caudal = MonitorCaudal()    
    monitor_alarmas = MonitorAlarmas()
    monitor_respuesta = MonitorRespuesta()

    # 3. Pasar el sistema al motor de simulación
    simulador = Coordinator(sistema)

    # 4. Definir la función de trazado para los monitores
    def tracer(event):
        print(f"EVENTO: Tiempo={event.time:.2f}, Modelo='{event.model.name}', Puerto='{event.port.name}', Valor={event.value}")

        # El evento tiene: model, time, port, value
        monitor_caudal.observar_orden(event)
        monitor_caudal.observar_flujo(event)
        monitor_alarmas.observar_alarmas(event)
        monitor_respuesta.observar_orden(event)
        monitor_respuesta.observar_flujo(event)

    # 5. Asignar la función de trazado al simulador
    simulador = Coordinator(sistema)
    simulador.tracer = tracer
    # 6. Inicializan los componentes
    simulador.initialize()

    # 7. Configurar parámetros de ejecución
    TIEMPO_SIMULACION = 3600.0  
   
    # 8. Arrancar el motor de simulación
    print("=========================================")
    print(" INICIANDO SIMULACIÓN DE EVENTOS DISCRETOS")
    print("=========================================")

    simulador.simulate(TIEMPO_SIMULACION)

    print("=========================================")
    print(" SIMULACIÓN FINALIZADA CON ÉXITO")
    print("=========================================")

    # 9. Obtener y mostrar las métricas de los monitores
    print("\n--- MÉTRICAS RECOLECTADAS ---")

    print("\n[ Monitor de Caudal ]")
    metricas_caudal = monitor_caudal.obtener_metricas()
    print(f"  Caudales indicados registrados: {len(metricas_caudal['caudal_indicado'])}")
    print(f"  Caudales reales registrados: {len(metricas_caudal['caudal_real'])}")
    # print(metricas_caudal) # Descomentar para ver datos crudos

    print("\n[ Monitor de Alarmas ]")
    metricas_alarmas = monitor_alarmas.obtener_metricas()
    if not metricas_alarmas['alarmas']:
        print("  No se generaron alarmas durante la simulación.")
    else:
        print(f"  Total de alarmas generadas: {len(metricas_alarmas['alarmas'])}")
        for i, (tiempo, alarma) in enumerate(metricas_alarmas['alarmas']):
            print(f"    {i+1}. Tiempo: {tiempo:.2f}s - Alarma: {alarma}")

    print("\n[ Monitor de Tiempo de Respuesta de Ajuste ]")
    metricas_respuesta = monitor_respuesta.obtener_metricas()
    if not metricas_respuesta['tiempos_respuesta']:
        print("  No se completaron ajustes de caudal para medir respuesta.")
    else:
        print(f"  Ajustes de caudal medidos: {len(metricas_respuesta['tiempos_respuesta'])}")
        tiempos = metricas_respuesta['tiempos_respuesta']
        avg_tiempo = sum(tiempos) / len(tiempos)
        print(f"  Tiempo de respuesta promedio: {avg_tiempo:.4f}s")

    print("-----------------------------\n")

    