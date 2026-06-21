from lib import AccionBomba
#Monitores para metricas relacionadas a la bolsa de infusion

#Calcula el tiempo de respuesta desde que se dispara la alerta de fin de bolsa hasta que el controlador actua 
# (detiene la bomba o activa alarma) 
class MonitorBolsa:
    def __init__(self):
        self.tiempos_respuesta = []
        self.t_llegada_controlador = None
        self.llegada_fin_bolsa = []

    def observar_alerta_fin_bolsa(self, t,valor):
        #T1: El evento de fin de bolsa llega al puerto de entrada del controlador.
        self.t_llegada_controlador = t
        self.llegada_fin_bolsa.append((t, valor))
        

    def observar_accion_controlador(self, t,valor):
        #T2: El controlador emite el comando de apagado al actuador."""
        if self.t_llegada_controlador is not None and valor == AccionBomba.DETENER_BOMBA:
            latencia = t - self.t_llegada_controlador
            self.tiempos_respuesta.append(latencia)
            self.t_llegada_controlador = None

    def obtener_metricas(self):
        return {
            "tiempos_respuesta": self.tiempos_respuesta,
            "tiempos_llegada_fin_bolsa": self.llegada_fin_bolsa,
            "respuesta_promedio": self.obtener_tiempo_respuesta_promedio(), 
            "cantidad_datos": len(self.tiempos_respuesta)
            
        }
    
    def obtener_tiempo_respuesta_promedio(self):
        if not self.tiempos_respuesta:
            return 0
        return sum(self.tiempos_respuesta) / len(self.tiempos_respuesta)
