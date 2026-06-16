from sistema import SistemaInfusionAcoplado
from xdevs.sim import Coordinator
from monitores.monitor_caudal import MonitorCaudal
from monitores.monitor_alarmas import MonitorAlarmas
from monitores.monitor_respuesta import MonitorRespuesta
from monitores.monitor_controlador import MonitorControlador
from lib import AccionBomba
from simulacion import Simulacion

if __name__ == "__main__":

    def f():
        return 120.0
    def g():
        return 1000.0
    simular = Simulacion("SimulacionBombaInfusion")
    simular.iniciar_simulacion(3600.0,f,g)
    simular.mostrar_metricas()

    #Escenario 1: Funcionamiento normal sin fallas


    #Escenario 2: Cambia orden medica durante la infusion
    #el generador emite una orden de 50, y a los 2 segundo emite orden de 80... luego no deberia emitir nada por 30000 segundos
    valores_f = iter([50.0, 80.0])
    def f():
        return next(valores_f, 80.0)  # después sigue devolviendo 50

    valores_g = iter([10.0, 2.0, 30000.0])
    def g():
        return next(valores_g, 30000)
    simular = Simulacion("SimulacionBombaInfusion")
    simular.iniciar_simulacion(3600.0,f,g)
    simular.mostrar_metricas()

  