class MonitorRespuestaBolsa:
    def __init__(self):
        self.tiempos_respuesta = []
        self.tiempo_inicio_fin_bolsa = None
        self.esperando_parada = False

    def observar_evento(self, event):
        puerto = event.port
        
        # Asumimos que hay un componente que emite por un puerto llamado 'finBolsa'
        # cuando la bolsa se vacía. Este es el inicio de nuestra medición.
        if puerto.name == "finBolsa" and event.value[0] is True:
            if not self.esperando_parada:
                self.tiempo_inicio_fin_bolsa = event.time
                self.esperando_parada = True

        # Ahora, esperamos la reacción: el actuador debe ponerse en 0.
        # El 'tracer' captura la salida del actuador.
        elif puerto.name == "caudalReal" and self.esperando_parada:
            caudal_actual = event.value[0]
            if caudal_actual == 0.0:
                tiempo_respuesta = event.time - self.tiempo_inicio_fin_bolsa
                self.tiempos_respuesta.append(tiempo_respuesta)
                # Reseteamos para la proxima vez que ocurra el evento
                self.esperando_parada = False
                self.tiempo_inicio_fin_bolsa = None

    def obtener_metricas(self):
        return {
            "tiempos_respuesta_fin_bolsa": self.tiempos_respuesta
        }
