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
            # `caudal_actual` está en ml/h y `e` en segundos, convertir a horas
            consumo = self.caudal_actual * (e / 3600.0)
            self.volumen_actual = max(0.0, self.volumen_actual - consumo)

        # 2. Procesar nuevo caudal
        if not self.i_caudal.empty():
            self.caudal_actual = self.i_caudal.get()
            
            if self.caudal_actual > 0:
                tiempo_para_vaciado = self.volumen_actual / self.caudal_actual
                # Queremos disparar la alarma cuando falten 60 segundos.
                # Tiempo de espera = Tiempo total - 60
                tiempo_para_alarma = tiempo_para_vaciado - 60
                
                if tiempo_para_alarma <= 0:
                    # Ya pasamos el umbral o estamos en él, avisamos de inmediato
                    self.hold_in("vaciando", 0)
                else:
                    # Programamos el aviso para cuando falten exactamente 60s
                    self.hold_in("vaciando", tiempo_para_alarma)
            else:
                self.hold_in("pausada", INFINITY)

        # 3. Reset por confirmación
        elif not self.i_confirmacion.empty():
            if self.i_confirmacion.get() and self.volumen_actual <= 0:
                self.volumen_actual = CAPACIDAD_BOMBA
                self.caudal_actual = 0.0
                self.hold_in("llena", INFINITY)

    
    def exit(self):
        pass