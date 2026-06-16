from sistema import SistemaInfusionAcoplado
from xdevs.sim import Coordinator
from monitores.monitor_caudal import MonitorCaudal
from monitores.monitor_alarmas import MonitorAlarmas
from monitores.monitor_respuesta import MonitorRespuesta
from monitores.monitor_controlador import MonitorControlador
from lib import AccionBomba




class Simulacion():

    def __init__(self, name):

        self.sistema = SistemaInfusionAcoplado("Suite_Simulacion_Medica")
        self.monitor_caudal = MonitorCaudal()    
        self.monitor_alarmas = MonitorAlarmas()
        self.monitor_respuesta = MonitorRespuesta()
        self.monitor_controlador = MonitorControlador()
        self.tiempoSimulacion = 3600.0
        self.simulador = Coordinator(self.sistema)
   

    def iniciar_simulacion(self, tiempoSimulacion=3600.0, funcionCaudal=None, funcionTiempo=None):
        self.simulador.initialize()
        self.tiempoSimulacion = tiempoSimulacion

        #Configuraciones
        if funcionCaudal!=None: self.sistema.generador.setFuncionCaudal(funcionCaudal)
        if funcionTiempo!=None: self.sistema.generador.setFuncionTiempo(funcionTiempo)

        print("=========================================")
        print(" INICIANDO SIMULACIÓN DE EVENTOS DISCRETOS")
        print("=========================================")

        # 5. Loop de simulacion
        while self.simulador.clock.time < self.tiempoSimulacion:
            if self.simulador.time_next >= self.tiempoSimulacion:
                break

            self.simulador.lambdaf()
            t = self.simulador.time_next

            # ── Monitor caudal ────────────────────────────────────────
            if not self.sistema.generador.o_orden_medica.empty():
                v = self.sistema.generador.o_orden_medica.get()
                print(f"EVENTO: t={t:.2f}  ordenMedica  valor={v}")
                self.monitor_caudal.observar_orden(t, v)
                self.monitor_respuesta.observar_orden(t, v)

            if not self.sistema.sensor.o_sensor_flujo.empty():
                v = self.sistema.sensor.o_sensor_flujo.get()
                print(f"EVENTO: t={t:.2f}  sensorFlujo  valor={v:.2f}")
                self.monitor_caudal.observar_flujo(t, v)
                self.monitor_respuesta.observar_flujo(t, v)

            # ── Monitor alarmas ───────────────────────────────────────
            if not self.sistema.alarma.o_notificacion.empty():
                v = self.sistema.alarma.o_notificacion.get()
                print(f"EVENTO: t={t:.2f}  alarma       valor={v}")
                self.monitor_alarmas.observar_alarma(t, v)

            # ── Monitor controlador ───────────────────────────────────
            if not self.sistema.controlador.o_mensaje_actuador.empty():
                v = self.sistema.controlador.o_mensaje_actuador.get()
                print(f"EVENTO: t={t:.2f}  mensajeActuador  valor={v}")
                if(v==AccionBomba.DETENER_BOMBA):
                    self.monitor_controlador.observar_orden_apagar(t, 0.0)
                else:
                    self.monitor_controlador.observar_ajustar_caudal(t, v)
            
            if not self.sistema.controlador.o_alarma.empty():    
                v = self.sistema.controlador.o_alarma.get()
                print(f"EVENTO: t={t:.2f}  alarmaControlador  valor={v}")
                self.monitor_controlador.observar_alarma(t, v)

            self.simulador.deltfcn()
            self.simulador.clear()
            self.simulador.clock.time = self.simulador.time_next

        print("=========================================")
        print(" SIMULACIÓN FINALIZADA CON ÉXITO")
        print("=========================================")
        

    def mostrar_metricas(self):
  
        # 6. Obtener y mostrar las métricas de los monitores
        print("\n--- MÉTRICAS RECOLECTADAS ---")

        print("\n[ Monitor de Caudal ]")
        metricas_caudal = self.monitor_caudal.obtener_metricas()
        print(f"  Caudales indicados registrados: {len(metricas_caudal['caudal_indicado'])}")
        print(f"  Caudales reales registrados: {len(metricas_caudal['caudal_real'])}")
        #print(metricas_caudal) # Descomentar para ver datos crudos

        print("\n[ Monitor de Alarmas ]")
        metricas_alarmas = self.monitor_alarmas.obtener_metricas()
        if not metricas_alarmas['alarmas']:
            print("  No se generaron alarmas durante la simulación.")
        else:
            print(f"  Total de alarmas generadas: {len(metricas_alarmas['alarmas'])}")
            for i, (tiempo, alarma) in enumerate(metricas_alarmas['alarmas']):
                print(f"    {i+1}. Tiempo: {tiempo:.2f}s - Alarma: {alarma}")

        print("\n[ Monitor de Tiempo de Respuesta de Ajuste ]")
        metricas_respuesta = self.monitor_respuesta.obtener_metricas()
        if not metricas_respuesta['tiempos_respuesta']:
            print("  No se completaron ajustes de caudal para medir respuesta.")
        else:
            print(f"  Ajustes de caudal medidos: {len(metricas_respuesta['tiempos_respuesta'])}")
            tiempos = metricas_respuesta['tiempos_respuesta']
            avg_tiempo = sum(tiempos) / len(tiempos)
            print(f"  Tiempo de respuesta promedio: {avg_tiempo:.4f}s")

        
        print("\n[ Monitor del controlador ]")
        metricas_controlador = self.monitor_controlador.obtener_metricas()
        if not metricas_controlador['alarmas']:
            print("  No se detectaron salidas de alarma.")
        else:
            print(f"  Total de alarmas generadas: {len(metricas_controlador['alarmas'])}")
            for i, (tiempo, alarma) in enumerate(metricas_controlador['alarmas']):
                print(f"    {i+1}. Tiempo: {tiempo:.2f}s - Alarma: {alarma}")

        if not metricas_controlador['ajustarCaudal']:
            print("  No se detectaron ajustes de caudal.")
        else:   
            print(f"  Total de ajustes de caudal: {len(metricas_controlador['ajustarCaudal'])}")
            for i, (tiempo, caudal) in enumerate(metricas_controlador['ajustarCaudal']):
                print(f"    {i+1}. Tiempo: {tiempo:.2f}s - Caudal ajustado: {caudal}")

        if not metricas_controlador['ordenApagar']:
            print("  No se detecto apagado en la bomba.")
        else:   
            print(f"  Total ordenes de apagar: {len(metricas_controlador['ordenApagar'])}")
            for i, (tiempo, caudal) in enumerate(metricas_controlador['ordenApagar']):
                print(f"    {i+1}. Tiempo: {tiempo:.2f}s - Caudal ajustado: {caudal}")

        print("-----------------------------\n")



  