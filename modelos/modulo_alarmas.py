from xdevs.models import AtomicDEVS

class ModuloAlarmas(AtomicDEVS):
    def __init__(self, name):
        super().__init__(name)
        
        self.T_REPETIR = 10
        self.TOLERANCIA = 30
        
        self.addInPort("alarma")
        self.addInPort("confirmacionEnfermero")
        self.addOutPort("notificacion")
        
        # Estado inicial: (ninguna, infinito)
        self.nivel_activo = "ninguna"
        self.holdIn("ninguna", float('inf'))

    def extTransition(self, inputs):
        
        if "alarma" in inputs:
            x = inputs["alarma"][0]
            if x == "alarmaBaja":
                self.nivel_activo = "baja"
                self.holdIn("baja", 0)
            elif x == "alarmaMedia":
                self.nivel_activo = "media"
                self.holdIn("media", 0)
            elif x == "alarmaCritica":
                self.nivel_activo = "critica"
                self.holdIn("critica", 0)
                
        elif "confirmacionEnfermero" in inputs:
            x = inputs["confirmacionEnfermero"][0]
            if x == "confirmado" and self.nivel_activo in ["critica", "repeticionCritica"]:
                self.nivel_activo = "ninguna"
                self.holdIn("ninguna", float('inf'))
                
        return self.state

    def intTransition(self):
       
        if self.nivel_activo == "critica":
            self.nivel_activo = "repeticionCritica"
            self.holdIn("repeticionCritica", self.TOLERANCIA)
        elif self.nivel_activo == "repeticionCritica":
            self.nivel_activo = "repeticionCritica"
            self.holdIn("repeticionCritica", self.T_REPETIR)
        elif self.nivel_activo in ["baja", "media"]:
            self.nivel_activo = "ninguna"
            self.holdIn("ninguna", float('inf'))
            
        return self.state

    def outputFnc(self):
        # estado -> (puerto, [mensaje])
        if self.nivel_activo == "baja":
            return {self.getPort("notificacion"): ["alarmaBaja"]}
        elif self.nivel_activo == "media":
            return {self.getPort("notificacion"): ["alarmaMedia"]}
        elif self.nivel_activo in ["critica", "repeticionCritica"]:
            return {self.getPort("notificacion"): ["alarmaCritica"]}
        return {}   