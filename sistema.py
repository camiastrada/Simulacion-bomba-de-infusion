from modelos.generador_ordenes import GeneradorOrdenes
from modelos.sensor_flujo import SensorFlujo
from modelos.controlador import Controlador
from modelos.actuador import Actuador
from modelos.modulo_alarmas import ModuloAlarmas
from xdevs.models import Atomic, Coupled, Port, INFINITY
from xdevs.sim import Coordinator

class SistemaInfusionAcoplado(Coupled):
    """
    Representa la red o 'suite' completa del sistema de infusión.
    Conecta el entorno físico, el factor humano y el software de la bomba.
    """
    def __init__(self, nombre):
        super().__init__(nombre)
        
        # 1. INSTANCIAR TODOS LOS COMPONENTES 
        self.generador    = GeneradorOrdenes()
        self.sensor = SensorFlujo()
        self.controlador   = Controlador()
        self.actuador    = Actuador()
        self.alarma  = ModuloAlarmas()

        for comp in [self.generador, self.sensor, self.controlador, self.actuador, self.alarma]:
            self.add_component(comp)
        
        # 2. ACOPLAMIENTO DE PUERTOS (El "Cableado" del Sistema)
        # Conexion internas
        # El controlador envia un mensaja_actuador al actuador
        self.add_coupling(self.controlador.o_mensaje_actuador, self.actuador.i_mensaje_actuador)



        # Conexiones externas (irian las de la bolsa y confirmacion del enfermero)
        
