from xdevs.models import Atomic, Port, INFINITY

class ModuloAlarmas(Atomic):
    def __init__(self, name="modulo_alarmas"):
        super().__init__(name)
        
        self.T_REPETIR = 10.0
        self.TOLERANCIA = 30.0
        
        self.i_alarma = Port(str, "alarma")
        self.i_confirmacion = Port(str, "confirmacionEnfermero")
        self.o_notificacion = Port(str, "notificacion")
        
        self.add_in_port(self.i_alarma)
        self.add_in_port(self.i_confirmacion)
        self.add_out_port(self.o_notificacion)
        
        self.nivel_activo = "ninguna"

    def initialize(self):
        self.hold_in("ninguna", INFINITY)

    def exit(self):
        pass

    def lambdaf(self):
        if self.nivel_activo == "baja":
            self.o_notificacion.add("alarmaBaja")
        elif self.nivel_activo == "media":
            self.o_notificacion.add("alarmaMedia")
        elif self.nivel_activo in ["critica", "repeticionCritica"]:
            self.o_notificacion.add("alarmaCritica")

    def deltint(self):
        if self.nivel_activo == "critica":
            self.nivel_activo = "repeticionCritica"
            self.hold_in("repeticionCritica", self.TOLERANCIA)
        elif self.nivel_activo == "repeticionCritica":
            self.nivel_activo = "repeticionCritica"
            self.hold_in("repeticionCritica", self.T_REPETIR)
        elif self.nivel_activo in ["baja", "media"]:
            self.nivel_activo = "ninguna"
            self.hold_in("ninguna", INFINITY)
        else:
            self.hold_in(self.state, INFINITY)

    def deltext(self, e):
        
        if not self.i_alarma.empty():
            x = self.i_alarma.get()
            if x == "alarmaBaja":
                self.nivel_activo = "baja"
                self.hold_in("baja", 0)
            elif x == "alarmaMedia":
                self.nivel_activo = "media"
                self.hold_in("media", 0)
            elif x == "alarmaCritica":
                self.nivel_activo = "critica"
                self.hold_in("critica", 0)
                
        elif not self.i_confirmacion.empty():
            x = self.i_confirmacion.get()
            if x == "confirmado" and self.nivel_activo in ["critica", "repeticionCritica"]:
                self.nivel_activo = "ninguna"
                self.hold_in("ninguna", INFINITY)