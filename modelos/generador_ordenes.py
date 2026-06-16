import random
from xdevs.models import Atomic, Port
from lib import CAUDAL_MAX, CAUDAL_MIN

T_MIN_ORDEN = 10.0
T_MAX_ORDEN = 600.0

class GeneradorOrdenes(Atomic):

    def __init__(self, name="generador_ordenes"):
        super().__init__(name)
        self.o_orden_medica = Port(float, "ordenMedica")
        self.add_out_port(self.o_orden_medica)

        self.funEleccionCaudal = lambda: random.uniform(CAUDAL_MIN, CAUDAL_MAX)
        self.funEleccionTiempo = lambda: random.uniform(T_MIN_ORDEN, T_MAX_ORDEN)

    def initialize(self):
        self.caudal = self.funEleccionCaudal()
        self.hold_in("generando", self.funEleccionTiempo())

    def exit(self):
        pass

    def lambdaf(self):
        self.o_orden_medica.add(self.caudal)

    def setFuncionCaudal(self, funcion):
        self.funEleccionCaudal = funcion

    def setFuncionTiempo(self, funcion):
        self.funEleccionTiempo = funcion

    def deltint(self):
        self.caudal = self.funEleccionCaudal()
        self.hold_in("generando", self.funEleccionTiempo())

    def deltext(self, e):
        pass