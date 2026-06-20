import random 
from xdevs.models import Atomic, Port

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
        self.caudal = 0.0

    #Estado del sensor de flujo(caudal, sigma)
    def initialize(self):
        self.hold_in("muestreo", self.PERIODO)

    def exit(self):
        pass

    def lambdaf(self):
        
        if self.caudal <= 0:
            self.o_sensor_flujo.add(0.0)
        else:
            # Generar una variación aleatoria del caudal real para simular el ruido del sensor
            # Variación de ±2% del valor real, en caso estandar no ocurren variaciones grandes
            factor_variacion = 1 + random.uniform(-0.02, 0.02)  
            caudal_con_ruido = self.caudal * factor_variacion
            self.o_sensor_flujo.add(caudal_con_ruido)

    def deltint(self):
        self.hold_in("muestreo", self.PERIODO)

    #A efectos de la simulación, el sensor recibe las mediciones desde el actudor
    def deltext(self, e):
        if not self.i_caudal_actual.empty():
            self.caudal = self.i_caudal_actual.get()