from sistema import SistemaInfusionAcoplado
from xdevs.sim import Coordinator
from monitores.monitor_caudal import MonitorCaudal
from monitores.monitor_alarmas import MonitorAlarmas
from monitores.monitor_actualizacion_caudal import MonitorRespuesta
from monitores.monitor_controlador import MonitorControlador
from lib import AccionBomba
from simulacion import Simulacion

# Escenario 7: Alarma crítica - sensor mide mal, enfermero confirma tarde
   
def escenario7():
    def funcion_caudal_escenario7():
            return 2.0
        
    valores_t_emision = iter([1.0, 60000.0])
    def funcion_emision_orden_7():
            return next(valores_t_emision, 3000)


        # Sensor mide solo el 50% del caudal real → error de caudal garantizado
    def funcion_precision_error(x):
            return x * 0.5 
        
        # Enfermero confirma recién a los 90s (después de que escale a crítica)
    def t_confirmacion_tarde():
            return 60.0

    simular = Simulacion("SimulacionBombaInfusion")
    simular.iniciar_simulacion(
            200.0,
            funcion_caudal_escenario7,
            funcion_emision_orden_7   ,
            funcion_precision_error,   #fuerza el error de caudal
            t_confirmacion_tarde
        )
    simular.mostrar_metricas()
    simular.graficar_timeline("Escenario7_AlarmaCritica_ConfirmacionTarde")
    simular.graficar_caudal("Escenario7_AlarmaCritica_ConfirmacionTarde")
    simular.graficar_estado_bomba("Escenario7_AlarmaCritica_ConfirmacionTarde")

if __name__ == "__main__":

    simular = Simulacion("SimulacionBombaInfusion")
    simular.iniciar_simulacion(1000.0,None,None,None,None)
    simular.mostrar_metricas()
    simular.graficar_timeline()
    simular.graficar_caudal("Escenario1_Normal") 
    simular.graficar_estado_bomba("Escenario1_Normal")
    simular.contar_detenciones_preventivas()


    # #Escenario 1: Funcionamiento normal sin fallas


    # #Escenario 2: Cambia orden medica durante la infusion
    # #el generador emite una orden de 50, y a los 2 segundo emite orden de 80... luego no deberia emitir nada por 30000 segundos
    valores_f = iter([50.0, 80.0])
    def f():
         return next(valores_f, 80.0)  # después sigue devolviendo 80

    valores_g = iter([1.0, 2.0, 30000.0])
    def g():
        return next(valores_g, 3000)
    simular = Simulacion("SimulacionBombaInfusion")
    simular.iniciar_simulacion(36000.0,f,g,None,None)
    simular.mostrar_metricas()


    # Escenario 6: Fin de bolsa con confirmación del enfermero
    # Se fija caudal alto para vaciar la bolsa en un tiempo corto de simulación.
    # El enfermero confirma la alarma baja luego de 20s.
    def funcion_caudal_max():
         return 200.0

    valores_emision = iter([1.0, 60000.0])
    def funcion_emision_orden():
         return next(valores_emision, 3000)


    def t_confirmacion_enfermero():
        return 20.0

    simular = Simulacion("SimulacionBombaInfusion")
    simular.iniciar_simulacion(2000.0, funcion_caudal_max, funcion_emision_orden , None, t_confirmacion_enfermero)
    simular.mostrar_metricas()
    simular.graficar_timeline("Escenario6_FinBolsa_ConfirmacionEnfermero")
    simular.graficar_caudal("Escenario6_FinBolsa_ConfirmacionEnfermero")
    simular.graficar_estado_bomba("Escenario6_FinBolsa_ConfirmacionEnfermero")

    escenario7()

    # #Escenario 3 se genera orden 0.0
    # def f():
    #     return 0.0
    # simular = Simulacion("SimulacionBombaInfusion")
    # simular.iniciar_simulacion(3600.0,f,None)
    # simular.mostrar_metricas()  
  
    # simular.graficar_caudal("Escenario1_Normal") 


    
   
    