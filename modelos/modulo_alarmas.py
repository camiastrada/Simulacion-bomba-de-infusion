from xdevs.models import Atomic, Port, INFINITY
from lib import EstadoBomba, error_caudal, AccionBomba

#Módulo de alarmas de la bomba de infusión

class ModuloAlarmas(Atomic):

    def __init__(self, name="modulo_alarmas"):
        super().__init__(name)
        
        self.T_REPETIR = 10.0
        self.TOLERANCIA = 30.0
        
        self.i_alarma = Port(str, "alarma")
        self.i_confirmacion = Port(bool, "confirmacionEnfermero")
        self.o_notificacion = Port(str, "notificacion")
        #Puerto de entrada
        self.add_in_port(self.i_alarma)
        self.add_in_port(self.i_confirmacion)
        #Puerto de salida
        self.add_out_port(self.o_notificacion)
        
        self.nivel_activo = "ninguna"

    #Estado del módulo de alarmas(nivel_activo, sigma)
    def initialize(self):
        self.hold_in("ninguna", INFINITY)

    def exit(self):
        pass
    

    #Según el nivel de alarma activo, se envía la notificación correspondiente
    def lambdaf(self):
        if self.nivel_activo == "baja":
            self.o_notificacion.add("alarmaBaja")
        elif self.nivel_activo == "media":
            self.o_notificacion.add("alarmaMedia")
        elif self.nivel_activo in ["critica", "repeticionCritica"]:
            self.o_notificacion.add("alarmaCritica")

    def deltint(self):    
        if self.nivel_activo == "critica":
            #Si sonó la alarma crítica, pasa a estado repeticionCritica, y se programa para sonar en 30 segundos
            self.nivel_activo = "repeticionCritica"
            self.hold_in("repeticionCritica", self.TOLERANCIA)
        elif self.nivel_activo == "repeticionCritica":
            #En estado repeticionCritica, se mantiene el nivel activo como repeticionCritica y se programa para repetirse cada 10 segundos
            self.nivel_activo = "repeticionCritica"
            self.hold_in("repeticionCritica", self.T_REPETIR)
        elif self.nivel_activo in ["baja", "media"]:
            #Si ya sonó la alarma baja o media, se reestablece el nivel a "ninguno"
            self.nivel_activo = "ninguna"
            self.hold_in("ninguna", INFINITY)
        else:
            self.hold_in(self.state, INFINITY)

    def deltext(self, e):
        #Ingresa una alarma desde el controlador
        #Según la alarma, se establece el nivel activo y se programa para sonar inmediatamente
        if not self.i_alarma.empty():
            x = self.i_alarma.get()
            if x is EstadoBomba.ALARMA_BAJA:
                self.nivel_activo = "baja"
                self.hold_in("baja", 0)
            elif x is EstadoBomba.ALARMA_MEDIA:
                self.nivel_activo = "media"
                self.hold_in("media", 0)
            elif x is EstadoBomba.ALARMA_CRITICA:
                self.nivel_activo = "critica"
                self.hold_in("critica", 0)
                
        #Ingresa una confirmación desde el enfermero        
        elif not self.i_confirmacion.empty():
            x = self.i_confirmacion.get()
            print(f"Modulo de alarmas recibe confirmación del enfermero: {x}")
            if x and self.nivel_activo in ["critica", "repeticionCritica"]:
                #Si el estado actual era critica o repeticionCritica, y se confirma, se reestablece el nivel a "ninguna"
                self.nivel_activo = "ninguna"
                self.hold_in("ninguna", INFINITY)