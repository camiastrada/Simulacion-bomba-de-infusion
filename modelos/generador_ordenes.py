import random
from xdevs.models import Atomic, Coupled, Port, INFINITY
#from pypdevs.DEVS import AtomicDEVS
from lib import CAUDAL_MAX, CAUDAL_MIN

T_MIN_ORDEN = 10.0
T_MAX_ORDEN = 600.0

class GeneradorOrdenes(Atomic):
  
    def __init__(self, nombre):
        super().__init__(nombre)
        
        # Y: ordenMedica : Caudal
        self.ordenMedica = self.addOutPort("ordenMedica")
        
        # S: Caudal X Time (Representado como un diccionario de estado)
        # Estado inicial (caudal inicial, sigma inicial)
        self.state = {
            "caudal": random.uniform(CAUDAL_MIN, CAUDAL_MAX),
            "sigma": random.uniform(T_MIN_ORDEN, T_MAX_ORDEN)
        }

    def ta(self):
       
        return self.state["sigma"]

    def outputFnc(self):
        
        return {self.ordenMedica: [self.state["caudal"]]}

    def intTransition(self):
        
        nuevo_caudal = random.uniform(0.0, CAUDAL_MAX)
        nuevo_sigma = random.uniform(T_MIN_ORDEN, T_MAX_ORDEN)
        
        self.state["caudal"] = nuevo_caudal
        self.state["sigma"] = nuevo_sigma
        
        return self.state

    def extTransition(self, inputs):
       # no se ejecuta, se deifne por compatibilidad con el modelo, pero no se espera recibir entradas
        return self.state
