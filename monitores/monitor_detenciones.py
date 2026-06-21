from lib import EstadoBomba

class MonitorDetenciones:

    def __init__(self, ventana_media: float = 5.0, ventana_baja: float = 60.0):
        # Configuramos ventanas distintas según el tipo de alarma
        self._ventana_media = ventana_media      # Escalamiento media -> crítica
        self._ventana_baja = ventana_baja        # Alarma baja
        self._t_alarmas: list[tuple[float, EstadoBomba]] = []
        self._detenciones: list[tuple[float, str]] = []

    def observar_alarma(self, t: float, tipo: EstadoBomba) -> None:
        # Se debe guardar como tupla (t, tipo)
        self._t_alarmas.append((t, tipo))

    def observar_detencion(self, t: float) -> None:
        es_preventiva = False
        
        for t_a, tipo in self._t_alarmas:
            if tipo == EstadoBomba.ALARMA_BAJA and (t - self._ventana_baja <= t_a <= t):
                es_preventiva = True
                break
            
           
            elif tipo in [EstadoBomba.ALARMA_MEDIA, EstadoBomba.ALARMA_CRITICA] and (t - self._ventana_media <= t_a <= t):
                es_preventiva = True
                break
                
        self._detenciones.append((t, 'preventiva' if es_preventiva else 'normal'))

    def obtener_metricas(self) -> dict:
        return {
            'detenciones':  self._detenciones,
            'total':        len(self._detenciones)
        }