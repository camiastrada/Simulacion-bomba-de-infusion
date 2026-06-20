class MonitorConfirmacion:
    def __init__(self):
        self.confirmaciones = []

    def observar_confirmacion(self, t, v):
        if v:
            self.confirmaciones.append((t, v))

    def obtener_metricas(self):
        return {'confirmaciones': self.confirmaciones}