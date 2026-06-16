class MonitorCaudal:
    def __init__(self):
        self.caudal_indicado = []
        self.caudal_real = []

    def observar_orden(self, t, valor):
        self.caudal_indicado.append((t, valor))

    def observar_flujo(self, t, valor):
        self.caudal_real.append((t, valor))

    def obtener_metricas(self):
        return {
            "caudal_indicado": self.caudal_indicado,
            "caudal_real": self.caudal_real
        }



