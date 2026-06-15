from xdevs.models import AtomicDEVS

class SensorFlujo(AtomicDEVS):
    def __init__(self, name):
        super().__init__(name)
        
        
        self.PERIODO = 1.0
        
        
        self.addInPort("caudalActual")
        self.addOutPort("sensorFlujo")
        
        
        self.caudal = 0.0
        self.holdIn("muestreo", self.PERIODO)

    def extTransition(self, inputs):
    
        if "caudalActual" in inputs:
            self.caudal = inputs["caudalActual"][0]
            tiempo_restante = self.sigma - self.elapsed
            self.holdIn("muestreo", tiempo_restante)
        return self.state

    def intTransition(self):
        
        self.holdIn("muestreo", self.PERIODO)
        return self.state

    def outputFnc(self):
        return {self.getPort("sensorFlujo"): [self.caudal]}