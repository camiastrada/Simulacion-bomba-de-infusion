from monitores.monitor_confirmacion import MonitorConfirmacion
from monitores.monitor_detenciones import MonitorDetenciones
from simulacion.visualizacion import Visualizacion
from sistema import SistemaInfusionAcoplado
from xdevs.sim import Coordinator
from monitores.monitor_caudal import MonitorCaudal
from monitores.monitor_alarmas import MonitorAlarmas
from monitores.monitor_actualizacion_caudal import MonitorRespuesta
from monitores.monitor_controlador import MonitorControlador
from monitores.monitor_bolsa import MonitorBolsa
from lib import AccionBomba




class Simulacion():

    def __init__(self, name):
        self.sistema = SistemaInfusionAcoplado("Suite_Simulacion_Medica")
        self.monitor_caudal = MonitorCaudal()    
        self.monitor_alarmas = MonitorAlarmas()
        self.monitor_respuesta = MonitorRespuesta()
        self.monitor_controlador = MonitorControlador()
        self.monitor_bolsa = MonitorBolsa()
        self.monitor_confirmacion = MonitorConfirmacion()
        self.tiempoSimulacion = 3600.0
        self.simulador = Coordinator(self.sistema)
        self.visualizacion = None 
        self.monitor_detenciones = MonitorDetenciones()
   

    def iniciar_simulacion(self, tiempoSimulacion=3600.0, funcionCaudal=None, funcionTiempo=None, funcionPrecisionCaudal=None, funcionTiempoConfirmacion=None):
        
        self.tiempoSimulacion = tiempoSimulacion

        #Configuraciones
        if funcionCaudal!=None: self.sistema.generador.setFuncionCaudal(funcionCaudal)
        if funcionTiempo!=None: self.sistema.generador.setFuncionTiempo(funcionTiempo)
        if funcionPrecisionCaudal!=None: self.sistema.sensor.setFuncionPrecision(funcionPrecisionCaudal)
        if funcionTiempoConfirmacion!=None: self.sistema.confirmacion.setFuncionTiempo(funcionTiempoConfirmacion)


        self.simulador.initialize()


        print("=========================================")
        print(" SIMULACIÓN DE EVENTOS DISCRETOS")
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
                self.monitor_caudal.observar_orden(t, v)
                self.monitor_respuesta.observar_orden(t, v)

            if not self.sistema.sensor.o_sensor_flujo.empty():
                v = self.sistema.sensor.o_sensor_flujo.get()
                self.monitor_caudal.observar_flujo(t, v)
                self.monitor_respuesta.observar_flujo(t, v)

            # ── Monitor alarmas ───────────────────────────────────────
            if not self.sistema.alarma.o_notificacion.empty():
                v = self.sistema.alarma.o_notificacion.get()
                self.monitor_alarmas.observar_alarma(t, v)
                self.monitor_detenciones.observar_alarma(t, v)        

            # ── Monitor controlador ───────────────────────────────────
            if not self.sistema.controlador.o_mensaje_actuador.empty():
                v = self.sistema.controlador.o_mensaje_actuador.get()
                if(v==AccionBomba.DETENER_BOMBA):
                    self.monitor_controlador.observar_orden_apagar(t, 0.0)
                    self.monitor_bolsa.observar_accion_controlador(t, v)
                    self.monitor_detenciones.observar_detencion(t)  
                else:
                    self.monitor_controlador.observar_ajustar_caudal(t, v)
            
            if not self.sistema.controlador.o_alarma.empty():    
                v = self.sistema.controlador.o_alarma.get()
                self.monitor_controlador.observar_alarma(t, v)
                
            # ── Monitor bolsa ───────────────────────────────────
            if not self.sistema.bolsa.o_fin_bolsa.empty():    
                v = self.sistema.bolsa.o_fin_bolsa.get()
                self.monitor_bolsa.observar_alerta_fin_bolsa(t, v)
            
            # ── Monitor confirmacion ──────────────────────────────────────
            
            if not self.sistema.confirmacion.o_confirmacion.empty():
                v = self.sistema.confirmacion.o_confirmacion.get()
                self.monitor_confirmacion.observar_confirmacion(t, v)
                
                
            self.simulador.deltfcn()
            self.simulador.clear()
            self.simulador.clock.time = self.simulador.time_next

        
        self.tiempoSimulacion= self.simulador.clock.time

        self.visualizacion = Visualizacion(
                        monitores={
                            'caudal':        self.monitor_caudal,
                            'alarmas':       self.monitor_alarmas,
                            'controlador':   self.monitor_controlador,
                            'confirmacion':  self.monitor_confirmacion,
                        },
                        tiempo_simulacion=self.tiempoSimulacion
                    )
        
    def graficar_metricas(self, titulo="Simulación"):
        if self.visualizacion is not None:
            self.visualizacion.graficar(titulo)
            
           

    def mostrar_metricas(self, descripcion_escenario="Simulación"):
  
        # Obtener y mostrar las métricas de los monitores
        print(descripcion_escenario)
        print("\n--- MÉTRICAS RECOLECTADAS ---")
       
        print("\n[ Monitor de Caudal ]")
        metricas_caudal = self.monitor_caudal.obtener_metricas()
        print(f"  Caudales indicados registrados: {len(metricas_caudal['caudal_indicado'])}")
        print(f"  Caudales reales registrados: {len(metricas_caudal['caudal_real'])}")

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
            print(f"  Tiempo de respuesta promedio: {metricas_respuesta['promedio_respuesta']}s")
        
        print("\n[ Monitor del controlador ]")
        metricas_controlador = self.monitor_controlador.obtener_metricas()
        if not metricas_controlador['alarmas']:
            print("  No se detectaron salidas de alarma.")
        else:
            print(f"  Total de alarmas generadas: {len(metricas_controlador['alarmas'])}")
           

        if not metricas_controlador['ajustarCaudal']:
            print("  No se detectaron ajustes de caudal.")
        else:   
            print(f"  Total de ajustes de caudal: {len(metricas_controlador['ajustarCaudal'])}")
            

        if not metricas_controlador['ordenApagar']:
            print("  No se detecto apagado en la bomba.")
        else:   
            print(f"  Total ordenes de apagar: {len(metricas_controlador['ordenApagar'])}")
            

        print("\n[ Monitor de la bolsa ]")
        print (f"  Total de alertas de fin de bolsa: {self.monitor_bolsa.obtener_cantidad_de_datos()}")
        print(f"  Tiempo de respuesta promedio desde alerta de fin de bolsa hasta acción del controlador: {self.monitor_bolsa.obtener_tiempo_respuesta_promedio():.4f}s")
       
        
        print("\n[ Monitor de detenciones ]")
        metricas_detenciones = self.monitor_detenciones.obtener_metricas()
        print(f"  Total de detenciones registradas: {metricas_detenciones['total']}")
        
        print("-----------------------------\n")

