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

    def initialize(self):
        self.caudal = random.uniform(CAUDAL_MIN, CAUDAL_MAX)
        self.hold_in("generando", random.uniform(T_MIN_ORDEN, T_MAX_ORDEN))

    def exit(self):
        pass

    def lambdaf(self):
        ###################PRINT DEBUG SACAR
        print(f"DEBUG: Generador enviando {self.caudal}")
        self.o_orden_medica.add(self.caudal)

    def deltint(self):
        self.caudal = random.uniform(0.0, CAUDAL_MAX)
        self.hold_in("generando", random.uniform(T_MIN_ORDEN, T_MAX_ORDEN))

    def deltext(self, e):
        pass