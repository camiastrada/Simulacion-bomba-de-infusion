class MonitorRespuesta:
    def __init__(self, precision=0.01):
        self.tiempos_respuesta = []
        self.ultima_orden = None
        self.tiempo_ultima_orden = None
        self.precision = precision

    def observar_orden(self, event):
        puerto = event.port
        if puerto.name == "ordenMedica":
            self.ultima_orden = event.value[0]
            self.tiempo_ultima_orden = event.time
            # Marcamos que estamos esperando que se alcance este caudal
            self.esperando_confirmacion = True

    def observar_flujo(self, event):
        puerto = event.port
        if puerto.name == "sensorFlujo" and self.ultima_orden is not None and self.esperando_confirmacion:
            caudal_actual = event.value[0]
            tiempo_actual = event.time
            
            # Comparamos si el caudal actual está dentro de un margen de precisión de la orden
            if abs(caudal_actual - self.ultima_orden) <= self.precision:
                tiempo_respuesta = tiempo_actual - self.tiempo_ultima_orden
                self.tiempos_respuesta.append(tiempo_respuesta)
                # Una vez que se alcanza, dejamos de esperar para no registrar múltiples tiempos para la misma orden
                self.esperando_confirmacion = False

    def obtener_metricas(self):
        return {
            "tiempos_respuesta": self.tiempos_respuesta
        }
