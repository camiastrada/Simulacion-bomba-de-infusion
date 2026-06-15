class MonitorCaudal:
    def __init__(self):
        self.caudal_indicado = []
        self.caudal_real = []

    def observar_orden(self, event):
        puerto = event.port
        if puerto.name == "ordenMedica":
            valor = event.value[0]
            tiempo = event.time
            self.caudal_indicado.append((tiempo, valor))

    def observar_flujo(self, event):
        puerto = event.port
        if puerto.name == "sensorFlujo":
            valor = event.value[0]
            tiempo = event.time
            self.caudal_real.append((tiempo, valor))

    def obtener_metricas(self):
        return {
            "caudal_indicado": self.caudal_indicado,
            "caudal_real": self.caudal_real
        }
