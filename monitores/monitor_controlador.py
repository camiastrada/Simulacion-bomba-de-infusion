class MonitorControlador:
    def __init__(self):
        self.alarmas = []
        self.ordenApagar = []
        self.ajustarCaudal = []

    def observar_alarma(self, t, valor):
        self.alarmas.append((t, valor))
    
    def observar_orden_apagar(self, t, valor):
        self.ordenApagar.append((t, valor))

    def observar_ajustar_caudal(self, t, valor):    
        self.ajustarCaudal.append((t, valor))

    def obtener_metricas(self): 
        return {
            "alarmas": self.alarmas,
            "ordenApagar": self.ordenApagar,
            "ajustarCaudal": self.ajustarCaudal
        }
