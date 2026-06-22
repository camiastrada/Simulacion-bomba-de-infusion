#Monitor para medir el tiempo de respuesta del sistema desde que llega una orden al controlador 
# hasta que el sensor refleja el cambio en el caudal

from lib import AccionBomba


class MonitorRespuesta:
    def __init__(self, precision=0.05):
        self.tiempos_respuesta = []
        self.ultima_orden = None
        self.tiempo_ultima_orden = None
        self.precision = precision
        self.esperando_confirmacion = False
        self.ordenes_interrumpidas = 0

    def observar_orden(self, t, valor):
        if self.esperando_confirmacion:
            self.ordenes_interrumpidas += 1  # llega una orden se cancela la anterior
            
        self.ultima_orden = valor
        self.tiempo_ultima_orden = t
        self.esperando_confirmacion = True

    def observar_flujo(self, t, valor):
        
        if self.ultima_orden is None or not self.esperando_confirmacion: #caso: no se espera ajuste por orden medica
            return
        if t <= self.tiempo_ultima_orden: #caso: el flujo se mide antes de la orden medica
            return
        
        if self.ultima_orden == 0.0:
            # para caudal cero, confirmar cuando el sensor mide casi cero
            confirmado = valor < 0.1
        else:
            # error relativo para caudal distinto de cero
            confirmado = abs(valor - self.ultima_orden) / self.ultima_orden <= self.precision
        
        if confirmado:
            self.tiempos_respuesta.append(t - self.tiempo_ultima_orden)
            self.esperando_confirmacion = False
            
            
    def observar_actuador(self, t, mensaje): #logica para descartar ordenes interrumpidas por detencion de bomba
        if mensaje == AccionBomba.DETENER_BOMBA:
            if self.esperando_confirmacion:
                self.ordenes_interrumpidas += 1  # métrica separada
            self.esperando_confirmacion = False
            self.ultima_orden = None
            
    def obtener_metricas(self):
        return {
            "tiempos_respuesta": self.tiempos_respuesta,
            "promedio_respuesta": self.promedio(),
            "ordenes_interrumpidas": self.ordenes_interrumpidas
        }
        
    def promedio(self):
        if not self.tiempos_respuesta:
            return 0
        return sum(self.tiempos_respuesta) / len(self.tiempos_respuesta)
    
    def obtener_cantidad_de_datos(self):
        return len(self.tiempos_respuesta)
    
    def obtener_tiempo_respuesta_promedio(self):
        if not self.tiempos_respuesta:
            return 0
        return sum(self.tiempos_respuesta) / len(self.tiempos_respuesta)


  