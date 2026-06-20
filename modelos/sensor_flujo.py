from xdevs.models import Atomic, Port
import random

# Sensor de flujo de la bomba de infusión

class SensorFlujo(Atomic):
    def __init__(self, name="sensor_flujo"):
        super().__init__(name)
        self.i_caudal_actual = Port(float, "caudalActual")
        self.o_sensor_flujo = Port(float, "sensorFlujo")
        #Puerto de entrada
        self.add_in_port(self.i_caudal_actual)
        #Puerto de salida
        self.add_out_port(self.o_sensor_flujo)


        self.PERIODO = 1.0
        self.fun_precision =  lambda x: random.uniform(x * 0.95, x * 1.05)
        self.caudal = 0.0

    #Estado del sensor de flujo(caudal, sigma)
    def initialize(self):
        self.hold_in("muestreo", self.PERIODO)

    def exit(self):
        pass

    def lambdaf(self):
        self.o_sensor_flujo.add(self.caudal)

    def deltint(self):
        self.hold_in("muestreo", self.PERIODO)

    #A efectos de la simulación, el sensor recibe las mediciones desde el actudor
    def deltext(self, e):
        if not self.i_caudal_actual.empty():
            self.caudal = self.fun_precision(self.i_caudal_actual.get())

    def setFuncionPrecision(self, funcion):
        self.fun_precision = funcion