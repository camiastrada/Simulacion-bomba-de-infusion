import random
from xdevs.models import Atomic, Port, INFINITY
from lib import CAUDAL_MAX, CAUDAL_MIN


#Generador de órdenes médicas de caudal para la bomba de infusión

class EnfermeroConfirmacion(Atomic):

    def __init__(self, name="generador_ordenes"):
        super().__init__(name)
        self.i_alerta_alarma = Port(str, "alertaAlarma")
        self.o_confirmacion = Port(bool, "confirmacion")
        #Puerto de salida
        self.add_in_port(self.i_alerta_alarma)
        self.add_out_port(self.o_confirmacion)

        #Funciones para generar cuanto tarda el efermero en confirmar una alarma
        self.tiempoProximaConfirmacion = lambda: random.uniform(0.5, 5.0)

    #Estado del generador de ordenes(alarmaActiva, sigma)
    def initialize(self):
        self.alarmaActiva = False
        self.hold_in("inactiva", INFINITY)

    def exit(self):
        pass

    def lambdaf(self): 
        print("Enfermero recibe alerta de alarma, y confirma la alarma")
        self.o_confirmacion.add(True)

    #Cambiar la funcion para eleccion de tiempo de respuesta del enfermero
    def setFuncionTiempo(self, funcion):
        self.tiempoProximaConfirmacion = funcion

    def deltint(self):
        self.alarmaActiva = False
        self.hold_in("inactiva", INFINITY)

    def deltext(self, e):
        print("Enfermero recibe mensaje de alerta de alarma")
        if not self.i_alerta_alarma.empty():
            if self.i_alerta_alarma.get() in {"alarmaCritica", "alarmaBaja"}:
                if not self.alarmaActiva:
                    # Primera vez que recibe la alarma → iniciar countdown
                    self.alarmaActiva = True
                    self.hold_in("activa", self.tiempoProximaConfirmacion())
                else:
                    # Ya está contando → solo descontar tiempo transcurrido
                    self.sigma -= e
                    self.hold_in("activa", self.sigma)