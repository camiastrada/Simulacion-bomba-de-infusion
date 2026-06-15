from xdevs.models import Atomic, Port, INFINITY
import random

class SensorFlujo(Atomic):
    def __init__(self, name="sensor_flujo"):
        super().__init__(name)
        self.i_caudal_actual = Port(float, "caudalActual")
        self.o_sensor_flujo = Port(float, "sensorFlujo")
        self.add_in_port(self.i_caudal_actual)
        self.add_out_port(self.o_sensor_flujo)
        self.PERIODO = 1.0
        self.caudal = 0.0

    def initialize(self):
        self.hold_in("muestreo", self.PERIODO)

    def exit(self):
        pass

    def lambdaf(self):
        self.o_sensor_flujo.add(self.caudal)

    def deltint(self):
        self.hold_in("muestreo", self.PERIODO)

    def deltext(self, e):
        if not self.i_caudal_actual.empty():
            self.caudal = self.i_caudal_actual.get()