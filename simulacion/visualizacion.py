import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from lib import EstadoBomba


# ── Constantes de presentación ────────────────────────────────────────────────

FILAS_TIMELINE = {
    'confirmacion':   (8, '#9B59B6', 'Confirmación enfermero'),
    'fin_bolsa':      (7, '#D4537E', 'Fin bolsa'),
    'ajuste_caudal':  (6, '#534AB7', 'Ajuste caudal'),
    'orden_medica':   (5, '#378ADD', 'Orden médica'),
    'sensor_flujo':   (4, '#1D9E75', 'Sensor flujo'),
    'alarma_critica': (3, '#E24B4A', 'Alarma crítica'),
    'alarma_media':   (2, '#EF9F27', 'Alarma media'),
    'alarma_baja':    (1, '#639922', 'Alarma baja'),
    'detener_bomba':  (0, '#A32D2D', 'Detener bomba'),
}

MAPA_ALARMA_STR = {
    'alarmaBaja':    'alarma_baja',
    'alarmaMedia':   'alarma_media',
    'alarmaCritica': 'alarma_critica',
}

MAPA_ALARMA_ENUM = {
    EstadoBomba.ALARMA_BAJA:    'alarma_baja',
    EstadoBomba.ALARMA_MEDIA:   'alarma_media',
    EstadoBomba.ALARMA_CRITICA: 'alarma_critica',
}

COLORES_ALARMA_CAUDAL = {
    'alarmaBaja':    ('#f59e0b', 'Alarma baja'),
    'alarmaMedia':   ('#f97316', 'Alarma media'),
    'alarmaCritica': ('#dc2626', 'Alarma crítica'),
}

ESTADOS_BOMBA = {
    'SIN_ERROR':      (5, '#22c55e', 'Sin error'),
    'ALARMA_MEDIA':   (4, '#f97316', 'Alarma media'),
    'ALARMA_BAJA':      (3, '#f59e0b', 'Alarma baja'),
    'ALARMA_CRITICA': (2, '#9B59B6', 'Alarma crítica'),
    'APAGADO':        (1, '#dc2626', 'Apagado'),
}


class Visualizacion:

    def __init__(self, monitores: dict, tiempo_simulacion: float):
        """
        Parámetros
        ----------
        monitores : dict con claves 'caudal', 'alarmas', 'controlador', 'confirmacion'
        tiempo_simulacion : duración total de la simulación en segundos
        """
        self.monitores = monitores
        self.tiempo_simulacion = tiempo_simulacion

    # Gráfica general con todas las métricas
    def graficar(self, titulo: str = "Simulación") -> None:
        self.graficar_timeline(titulo)
        self.graficar_caudal(titulo)
        self.graficar_estado_bomba(titulo)
        plt.show()
        
    # ── Timeline ──────────────────────────────────────────────────────────────

    def graficar_timeline(self, titulo: str = "Simulación") -> None:
        metricas_c  = self.monitores['caudal'].obtener_metricas()
        metricas_a  = self.monitores['alarmas'].obtener_metricas()
        metricas_ct = self.monitores['controlador'].obtener_metricas()
        metricas_cf = self.monitores['confirmacion'].obtener_metricas()
        metricas_b  = self.monitores['fin_bolsa'].obtener_metricas()

        eventos = self._construir_eventos_timeline(
            metricas_c, metricas_a, metricas_ct, metricas_cf, metricas_b
        )

        fig, ax1 = plt.subplots(figsize=(14, 5))

        for tipo, (y, color, label) in FILAS_TIMELINE.items():
            ts = eventos[tipo]
            ax1.scatter(
                ts if ts else [],
                [y] * len(ts) if ts else [],
                color=color, s=60, label=label, zorder=3, linewidths=0,
            )

        # Caudal indicado en eje derecho
        ax2 = ax1.twinx()
        indicado = sorted(metricas_c.get('caudal_indicado', []), key=lambda p: p[0])
        if indicado:
            t_ind = [p[0] for p in indicado]
            v_ind = [p[1] for p in indicado]
            ax2.step(t_ind, v_ind, where='post', color='#378ADD',
                     linewidth=1.2, linestyle='--', alpha=0.5, label='Caudal indicado')
            ax2.set_ylabel('Caudal (ml/h)', color='#378ADD', fontsize=10)
            ax2.tick_params(axis='y', labelcolor='#378ADD')
            ax2.set_ylim(bottom=0)

        y_vals   = [v for v, _, _ in FILAS_TIMELINE.values()]
        y_labels = [label for _, _, label in FILAS_TIMELINE.values()]
        ax1.set_yticks(y_vals)
        ax1.set_yticklabels(y_labels, fontsize=9)
        ax1.set_ylim(-0.6, 8.6)
        ax1.set_xlabel('Tiempo (s)', fontsize=11)
        ax1.set_title(f'Timeline de eventos — {titulo}', fontsize=13)
        ax1.grid(axis='x', alpha=0.25)
        ax1.set_xlim(left=0, right=self.tiempo_simulacion)

        handles, labels = ax1.get_legend_handles_labels()
        ax1.legend(handles, labels, loc='upper right', fontsize=8, ncol=2, framealpha=0.7)

        plt.tight_layout()


    def _construir_eventos_timeline(self, metricas_c, metricas_a, metricas_ct, metricas_cf,metricas_b) -> dict:
        eventos = {k: [] for k in FILAS_TIMELINE}

        for t, _ in metricas_b.get('tiempos_llegada_fin_bolsa', []):
            eventos['fin_bolsa'].append(t)
            
        for t, _ in metricas_cf.get('confirmaciones', []):
            eventos['confirmacion'].append(t)

        for t, _ in metricas_c.get('caudal_indicado', []):
            eventos['orden_medica'].append(t)

        for t, _ in metricas_c.get('caudal_real', []):
            eventos['sensor_flujo'].append(t)

        for t, tipo in metricas_a.get('alarmas', []):
            clave = MAPA_ALARMA_STR.get(tipo)
            if clave:
                eventos[clave].append(t)

        for t, tipo in metricas_ct.get('alarmas', []):
            clave = MAPA_ALARMA_ENUM.get(tipo)
            if clave:
                eventos[clave].append(t)

        for t, _ in metricas_ct.get('ajustarCaudal', []):
            eventos['ajuste_caudal'].append(t)

        for t, _ in metricas_ct.get('ordenApagar', []):
            eventos['detener_bomba'].append(t)

        return eventos

    # ── Caudal ────────────────────────────────────────────────────────────────

    def graficar_caudal(self, titulo: str = "Simulación") -> None:
        metricas   = self.monitores['caudal'].obtener_metricas()
        metricas_a = self.monitores['alarmas'].obtener_metricas()

        indicado = sorted(metricas['caudal_indicado'], key=lambda p: p[0])
        real     = sorted(metricas['caudal_real'],     key=lambda p: p[0])

        if not indicado and not real:
            print("Sin datos de caudal para graficar.")
            return

        fig, ax = plt.subplots(figsize=(12, 5))

        ax.step(
            [p[0] for p in indicado], [p[1] for p in indicado],
            where='post', color='#2563eb', linewidth=2, label='Caudal indicado',
        )
        ax.plot(
            [p[0] for p in real], [p[1] for p in real],
            color='#dc2626', linewidth=1, linestyle='--', alpha=0.8,
            label='Caudal real (sensor)',
        )

        alarmas_graficadas = set()
        for t_a, tipo in metricas_a.get('alarmas', []):
            color, etiqueta = COLORES_ALARMA_CAUDAL.get(tipo, ('#999', tipo))
            label = etiqueta if tipo not in alarmas_graficadas else None
            ax.axvline(x=t_a, color=color, linewidth=1.2, linestyle=':', alpha=0.7, label=label)
            alarmas_graficadas.add(tipo)

        ax.set_xlabel('Tiempo (s)', fontsize=11)
        ax.set_ylabel('Caudal (ml/h)', fontsize=11)
        ax.set_title(f'Caudal indicado vs. caudal real — {titulo}', fontsize=13)
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(left=0)
        ax.set_ylim(bottom=0)

        plt.tight_layout()

    # ── Estado de la bomba ────────────────────────────────────────────────────

    def graficar_estado_bomba(self, titulo: str = "Simulación") -> None:
        
        metricas = self.monitores['controlador'].obtener_metricas()
        eventos  = self._construir_eventos_bomba(metricas)

        if not eventos:
            print("Sin eventos de estado para graficar.")
            return

        fig, ax = plt.subplots(figsize=(12, 4))

        for i, (t, estado) in enumerate(eventos):
            t_siguiente = eventos[i + 1][0] if i + 1 < len(eventos) else self.tiempo_simulacion
            y, color, _ = ESTADOS_BOMBA[estado]
            ax.fill_between(
                [t, t_siguiente], [y - 0.4, y - 0.4], [y + 0.4, y + 0.4],
                color=color, alpha=0.35,
            )
            ax.hlines(y, t, t_siguiente, colors=color, linewidth=3)

        leyenda = [
            Line2D([0], [0], color=color, linewidth=3, label=label)
            for _, (_, color, label) in ESTADOS_BOMBA.items()
        ]
        ax.legend(handles=leyenda, loc='upper right', fontsize=9)

        y_ticks  = [y     for y, _, _     in ESTADOS_BOMBA.values()]
        y_labels = [label for _, _, label in ESTADOS_BOMBA.values()]
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_labels, fontsize=10)
        ax.set_xlabel('Tiempo (s)', fontsize=11)
        ax.set_title(f'Estado de la bomba — {titulo}', fontsize=13)
        ax.set_xlim(0, self.tiempo_simulacion)
        ax.set_ylim(0.4, 5.6)
        ax.grid(axis='x', alpha=0.3)
        plt.tight_layout()

    def _construir_eventos_bomba(self, metricas: dict) -> list:
        
        eventos = []

        for t, _ in metricas['ajustarCaudal']:
            eventos.append((t, 'SIN_ERROR'))
        for t, _ in metricas['ordenApagar']:
            eventos.append((t, 'APAGADO'))
        for t, tipo in metricas['alarmas']:
            if tipo == EstadoBomba.ALARMA_MEDIA:
                eventos.append((t, 'ALARMA_MEDIA'))
            elif tipo == EstadoBomba.ALARMA_CRITICA:
                eventos.append((t, 'ALARMA_CRITICA'))
            elif tipo == EstadoBomba.ALARMA_BAJA:
                eventos.append((t, 'ALARMA_BAJA'))

        eventos.sort(key=lambda e: e[0])
        return eventos