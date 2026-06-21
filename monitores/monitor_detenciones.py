# monitores/monitor_detenciones.py
from lib import EstadoBomba

class MonitorDetenciones:

    def __init__(self, ventana_preventiva: float = 10.0):
        self._ventana = ventana_preventiva
        self._t_alarmas_criticas: list[float] = []
        self._detenciones: list[tuple[float, str]] = []  # (t, 'preventiva'|'normal')

    def observar_alarma(self, t: float, tipo) -> None:
        if tipo == EstadoBomba.ALARMA_CRITICA:
            self._t_alarmas_criticas.append(t)

    def observar_detencion(self, t: float) -> None:
        es_preventiva = any(
            t - self._ventana <= t_a <= t
            for t_a in self._t_alarmas_criticas
        )
        self._detenciones.append((t, 'preventiva' if es_preventiva else 'normal'))

    def obtener_metricas(self) -> dict:
        return {
            'detenciones':  self._detenciones,
            'total':        len(self._detenciones),
            'preventivas':  sum(1 for _, tipo in self._detenciones if tipo == 'preventiva'),
            'normales':     sum(1 for _, tipo in self._detenciones if tipo == 'normal'),
        }