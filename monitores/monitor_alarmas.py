class MonitorAlarmas:
    def __init__(self):
        self.alarmas = []

    def observar_alarmas(self, event):
        puerto = event.port
        if puerto.name == "notificacion":
            valor = event.value[0]
            tiempo = event.time
            self.alarmas.append((tiempo, valor))

    def obtener_metricas(self):
        return {
            "alarmas": self.alarmas
        }
