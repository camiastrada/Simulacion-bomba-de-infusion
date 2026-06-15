from modelos.generador_ordenes import GeneradorOrdenes
from modelos.sensor_flujo import SensorFlujo
from modelos.controlador import Controlador
from modelos.actuador import Actuador
from modelos.modulo_alarmas import ModuloAlarmas
from xdevs.models import Coupled

class SistemaInfusionAcoplado(Coupled):
    """
    Representa la red o 'suite' completa del sistema de infusión.
    Conecta el entorno físico, el factor humano y el software de la bomba.
    """
    def __init__(self, name):
        super().__init__(name)
        
        # 1. INSTANCIAR TODOS LOS COMPONENTES 
        self.generador = GeneradorOrdenes(name="generador")
        self.sensor = SensorFlujo(name="sensor")
        self.controlador = Controlador(name="controlador")
        self.actuador = Actuador(name="actuador")
        self.alarma = ModuloAlarmas(name="alarma")

        # 2. AÑADIR COMPONENTES AL SISTEMA ACOPLADO
        self.add_component(self.generador)
        self.add_component(self.sensor)
        self.add_component(self.controlador)
        self.add_component(self.actuador)
        self.add_component(self.alarma)
        
        # 3. DEFINIR LAS CONEXIONES (COUPLINGS)
        # La orden del generador va al controlador
        self.add_coupling(self.generador.o_orden_medica, self.controlador.i_orden_medica)
        
        # El controlador le dice al actuador qué hacer
        self.add_coupling(self.controlador.o_mensaje_actuador, self.actuador.i_mensaje_actuador)
        
        # El actuador produce un caudal real, que es medido por el sensor
        # ¡ESTA ES LA CONEXIÓN CLAVE QUE FALTABA!
        self.add_coupling(self.actuador.o_caudal_real, self.sensor.i_caudal_actual)
        
        # El sensor envía su medición de vuelta al controlador, cerrando el ciclo
        self.add_coupling(self.sensor.o_sensor_flujo, self.controlador.i_caudal_real)
        
        # El controlador puede enviar alarmas al módulo de alarmas
        self.add_coupling(self.controlador.o_alarma, self.alarma.i_alarma)
        
        # FALTAN Conexiones externas (irian las de la bolsa y confirmacion del enfermero)