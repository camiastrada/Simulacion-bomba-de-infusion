import random
from xdevs.models import Atomic, Port
from lib import CAUDAL_MAX, CAUDAL_MIN

T_MIN_ORDEN = 10.0
T_MAX_ORDEN = 600.0

#Generador de órdenes médicas de caudal para la bomba de infusión

class GeneradorOrdenes(Atomic):

    def __init__(self, name="generador_ordenes"):
        super().__init__(name)
        self.o_orden_medica = Port(float, "ordenMedica")
        #Puerto de salida
        self.add_out_port(self.o_orden_medica)

        #Funciones para generar un numero de caudal y tiempo para las ordenes
        self.funEleccionCaudal = lambda: random.uniform(CAUDAL_MIN, CAUDAL_MAX)
        self.funEleccionTiempo = lambda: random.uniform(T_MIN_ORDEN, T_MAX_ORDEN)

    #Estado del generador de ordenes(caudal, sigma)
    def initialize(self):
        self.caudal = self.funEleccionCaudal()
        self.hold_in("generando", self.funEleccionTiempo())

    def exit(self):
        pass

    def lambdaf(self):
        self.o_orden_medica.add(self.caudal)

    #Cambiar la funcion para eleccion de caudal
    def setFuncionCaudal(self, funcion):
        self.funEleccionCaudal = funcion
    #Cambiar la funcion para eleccion de tiempo entre ordenes
    def setFuncionTiempo(self, funcion):
        self.funEleccionTiempo = funcion

    def deltint(self):
        self.caudal = self.funEleccionCaudal()
        self.hold_in("generando", self.funEleccionTiempo())

    def deltext(self, e):
        pass