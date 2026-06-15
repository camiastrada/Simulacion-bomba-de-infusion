import random
from xdevs.models import AtomicDEVS
from lib import CAUDAL_MAX, CAUDAL_MIN

T_MIN_ORDEN = 10.0
T_MAX_ORDEN = 600.0

class GeneradorOrdenes(Atomic):
  
    def __init__(self, nombre):
        super().__init__(nombre)
        
       
        self.addOutPort("ordenMedica")
        
        
        self.caudal = random.uniform(CAUDAL_MIN, CAUDAL_MAX)
        self.sigma = random.uniform(T_MIN_ORDEN, T_MAX_ORDEN)
        
    
        self.holdIn("generando", self.sigma)

    def outputFnc(self):
        return {self.getPort("ordenMedica"): [self.caudal]}

    def intTransition(self):
        
        self.caudal = random.uniform(0.0, CAUDAL_MAX)
        self.sigma = random.uniform(T_MIN_ORDEN, T_MAX_ORDEN)
        
        
        self.holdIn("generando", self.sigma)
        return self.state

    def extTransition(self, inputs):
        return self.state