#Monitor para medir el tiempo de respuesta del sistema desde que llega una orden al controlador 
# hasta que el sensor refleja el cambio en el caudal
class MonitorRespuesta:
    def __init__(self, precision=0.05):
        self.tiempos_respuesta = []
        self.ultima_orden = None
        self.tiempo_ultima_orden = None
        self.precision = precision
        self.esperando_confirmacion = False

    def observar_orden(self, t, valor):
        self.ultima_orden = valor
        self.tiempo_ultima_orden = t
        self.esperando_confirmacion = True

    def observar_flujo(self, t, valor):
        if self.ultima_orden is not None and self.esperando_confirmacion:
            if abs(valor - self.ultima_orden) <= self.precision:
                tiempo_respuesta = t - self.tiempo_ultima_orden
                self.tiempos_respuesta.append(tiempo_respuesta)
                self.esperando_confirmacion = False

    def obtener_metricas(self):
        return {
            "tiempos_respuesta": self.tiempos_respuesta,
            "promedio_respuesta": self.promedio(),
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


  