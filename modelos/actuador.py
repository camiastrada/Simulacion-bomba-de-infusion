from xdevs.models import Atomic, Coupled, Port, INFINITY
from xdevs.sim import Coordinator
from lib import DELAY_ACTUADOR, AccionBomba

#Actuador de la bomba
class Actuador(Atomic):
    def __init__(self, name="actuador"):
        super().__init__(name)
        self.i_mensaje_actuador = Port(object, "mensajeActuador")
        self.o_caudal_real = Port(float, "caudalReal")
        self.add_in_port(self.i_mensaje_actuador)
        self.add_out_port(self.o_caudal_real)
    
    def initialize(self):    
        self.caudal_pendiente = 0.0
        self.hold_in("pasivo", INFINITY)

    def exit(self): pass

    def lambdaf(self):
        self.o_caudal_real.add(self.caudal_pendiente)
        print(f"DEBUG: Llega a actuador")
        
    def deltint(self):
        self.hold_in("pasivo", INFINITY)
    
    def deltext(self, e):
        if (self.i_mensaje_actuador.get()== AccionBomba.DETENER_BOMBA):
            self.caudal_pendiente = 0.0
            self.hold_in("deteniendo", DELAY_ACTUADOR)
        else:
            self.caudal_pendiente = self.i_mensaje_actuador.get()
            self.hold_in("ajustando", DELAY_ACTUADOR)
