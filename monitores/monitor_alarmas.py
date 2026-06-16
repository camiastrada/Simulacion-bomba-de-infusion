class MonitorAlarmas:
    def __init__(self):
        self.alarmas = []

    def observar_alarma(self, t, valor):
        self.alarmas.append((t, valor))

    def obtener_metricas(self):
        return {
            "alarmas": self.alarmas
        }
    
   
