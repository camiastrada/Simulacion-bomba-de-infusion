from xdevs.models import Atomic, Port, INFINITY
from lib import CAPACIDAD_BOMBA
class BolsaDeInfusion(Atomic):
    def __init__(self, name="bolsa"):
        super().__init__(name)
        
        self.i_caudal = Port(float, "caudal")
        self.i_confirmacion = Port(bool, "confirmacionEnfermero")
        
        # Salida: alerta cuando faltan <= 60 seg
        self.o_fin_bolsa = Port(bool, "finBolsa")
        
        self.add_in_port(self.i_caudal)
        self.add_in_port(self.i_confirmacion)
        self.add_out_port(self.o_fin_bolsa)

        
        self.volumen_actual = CAPACIDAD_BOMBA
        self.caudal_actual = 0.0

    def initialize(self):
        self.volumen_actual = CAPACIDAD_BOMBA
        self.caudal_actual = 0.0
        self.hold_in("llena", INFINITY)

    def lambdaf(self):
        self.o_fin_bolsa.add(True)

    def deltint(self):
        self.hold_in("aviso_enviado", INFINITY)

    def deltext(self, e):
        # 1. Actualizar volumen consumido
        # Cuando el caudal llega a 0 o es negativo ya se dio aviso de fin bolsa. 
        # Detener la bolsa es trabajo del controlador 
        if self.caudal_actual > 0:
            consumo = self.caudal_actual * (e / 3600.0)
            self.volumen_actual = max(0.0, self.volumen_actual - consumo)

        if not self.i_caudal.empty():
                nuevo_caudal = self.i_caudal.get()
            
                if nuevo_caudal != self.caudal_actual:
                    # Solo recalcular sigma si el caudal cambió
                    self.caudal_actual = nuevo_caudal
                    if self.caudal_actual > 0:
                        tiempo_vaciado = (self.volumen_actual / self.caudal_actual) * 3600.0
                        self.hold_in("vaciando", max(0.0, tiempo_vaciado - 60.0))
                    else:
                        self.hold_in("pausada", INFINITY)
                else:
                    # Caudal no cambió: solo actualizar sigma sin reiniciarlo
                    self.sigma -= e  
                    self.hold_in(self.phase, self.sigma)
                    
              
        # 3. Reset por confirmación
        elif not self.i_confirmacion.empty():
            
            if self.i_confirmacion.get():
                self.volumen_actual = CAPACIDAD_BOMBA
                self.hold_in("llena", INFINITY)

    
    def exit(self):
        pass