from sistema import SistemaInfusionAcoplado
from xdevs.sim import Coordinator
from monitores.monitor_caudal import MonitorCaudal
from monitores.monitor_alarmas import MonitorAlarmas
from monitores.monitor_actualizacion_caudal import MonitorRespuesta
from monitores.monitor_controlador import MonitorControlador
from monitores.monitor_bolsa import MonitorBolsa
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from lib import AccionBomba
from lib import EstadoBomba



class Simulacion():

    def __init__(self, name):
        self.sistema = SistemaInfusionAcoplado("Suite_Simulacion_Medica")
        self.monitor_caudal = MonitorCaudal()    
        self.monitor_alarmas = MonitorAlarmas()
        self.monitor_respuesta = MonitorRespuesta()
        self.monitor_controlador = MonitorControlador()
        self.monitor_bolsa = MonitorBolsa()
        self.tiempoSimulacion = 3600.0
        self.simulador = Coordinator(self.sistema)
   

    def iniciar_simulacion(self, tiempoSimulacion=3600.0, funcionCaudal=None, funcionTiempo=None, funcionPresicionCaudal=None, funcionTiempoConfirmacion=None):
        
        self.tiempoSimulacion = tiempoSimulacion

        #Configuraciones
        if funcionCaudal!=None: self.sistema.generador.setFuncionCaudal(funcionCaudal)
        if funcionTiempo!=None: self.sistema.generador.setFuncionTiempo(funcionTiempo)
        if funcionPresicionCaudal!=None: self.monitor_respuesta.precision = funcionPresicionCaudal
        if funcionTiempoConfirmacion!=None: self.sistema.sensor.setFuncionTiempoConfirmacion(funcionTiempoConfirmacion)


        self.simulador.initialize()


        print("=========================================")
        print(" INICIANDO SIMULACIÓN DE EVENTOS DISCRETOS")
        print("=========================================")

        # 5. Loop de simulacion
        while self.simulador.clock.time < self.tiempoSimulacion:
            if self.simulador.time_next >= self.tiempoSimulacion:
                break

            self.simulador.lambdaf()
            t = self.simulador.time_next

            # ── Monitor caudal ────────────────────────────────────────
            if not self.sistema.generador.o_orden_medica.empty():
                v = self.sistema.generador.o_orden_medica.get()
                self.monitor_caudal.observar_orden(t, v)
                self.monitor_respuesta.observar_orden(t, v)

            if not self.sistema.sensor.o_sensor_flujo.empty():
                v = self.sistema.sensor.o_sensor_flujo.get()
                self.monitor_caudal.observar_flujo(t, v)
                self.monitor_respuesta.observar_flujo(t, v)

            # ── Monitor alarmas ───────────────────────────────────────
            if not self.sistema.alarma.o_notificacion.empty():
                v = self.sistema.alarma.o_notificacion.get()
                self.monitor_alarmas.observar_alarma(t, v)

            # ── Monitor controlador ───────────────────────────────────
            if not self.sistema.controlador.o_mensaje_actuador.empty():
                v = self.sistema.controlador.o_mensaje_actuador.get()
                if(v==AccionBomba.DETENER_BOMBA):
                    self.monitor_controlador.observar_orden_apagar(t, 0.0)
                    self.monitor_bolsa.observar_accion_controlador(t, v)
                else:
                    self.monitor_controlador.observar_ajustar_caudal(t, v)
            
            if not self.sistema.controlador.o_alarma.empty():    
                v = self.sistema.controlador.o_alarma.get()
                self.monitor_controlador.observar_alarma(t, v)
                
            # ── Monitor bolsa ───────────────────────────────────
            if not self.sistema.bolsa.o_fin_bolsa.empty():    
                v = self.sistema.bolsa.o_fin_bolsa.get()
                self.monitor_bolsa.observar_alerta_fin_bolsa(t, v)
            

            self.simulador.deltfcn()
            self.simulador.clear()
            self.simulador.clock.time = self.simulador.time_next

        print("=========================================")
        print(" SIMULACIÓN FINALIZADA CON ÉXITO")
        print("=========================================")
        
    def graficar_timeline(self, titulo="Simulación"):
        fig, ax1 = plt.subplots(figsize=(14, 5))

        FILAS = {
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

        metricas_c  = self.monitor_caudal.obtener_metricas()
        metricas_a  = self.monitor_alarmas.obtener_metricas()
        metricas_ct = self.monitor_controlador.obtener_metricas()

        eventos = {k: [] for k in FILAS}

        for t, _ in metricas_c.get('caudal_indicado', []):
            eventos['orden_medica'].append(t)
        for t, _ in metricas_c.get('caudal_real', []):
            eventos['sensor_flujo'].append(t)

        # monitor_alarmas → strings
        for t, tipo in metricas_a.get('alarmas', []):
            clave = MAPA_ALARMA_STR.get(tipo)
            if clave:
                eventos[clave].append(t)

        # monitor_controlador → EstadoBomba
        for t, tipo in metricas_ct.get('alarmas', []):
            clave = MAPA_ALARMA_ENUM.get(tipo)
            if clave:
                eventos[clave].append(t)

        for t, _ in metricas_ct.get('ajustarCaudal', []):
            eventos['ajuste_caudal'].append(t)
        for t, _ in metricas_ct.get('ordenApagar', []):
            eventos['detener_bomba'].append(t)

        # ── Scatter por fila ─────────────────────────────────────────────────
        for tipo, (y, color, label) in FILAS.items():
            ts = eventos[tipo]
            ax1.scatter(
                ts if ts else [],
                [y] * len(ts) if ts else [],
                color=color, s=60, label=label, zorder=3, linewidths=0
            )

        # ── Caudal indicado como escalón (eje derecho) ───────────────────────
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

        # ── Ejes y etiquetas ─────────────────────────────────────────────────
        y_vals   = [v for v, _, _ in FILAS.values()]
        y_labels = [label for _, _, label in FILAS.values()]
        ax1.set_yticks(y_vals)
        ax1.set_yticklabels(y_labels, fontsize=9)
        ax1.set_ylim(-0.6, 7.6)
        ax1.set_xlabel('Tiempo (s)', fontsize=11)
        ax1.set_title(f'Timeline de eventos — {titulo}', fontsize=13)
        ax1.grid(axis='x', alpha=0.25)
        ax1.set_xlim(left=0, right=self.tiempoSimulacion)

        handles, labels = ax1.get_legend_handles_labels()
        ax1.legend(handles, labels, loc='upper right',
                fontsize=8, ncol=2, framealpha=0.7)

        plt.tight_layout()
        plt.show()   
    def mostrar_metricas(self):
  
        # Obtener y mostrar las métricas de los monitores
        print("\n--- MÉTRICAS RECOLECTADAS ---")

        print("\n[ Monitor de Caudal ]")
        metricas_caudal = self.monitor_caudal.obtener_metricas()
        print(f"  Caudales indicados registrados: {len(metricas_caudal['caudal_indicado'])}")
        print(f"  Caudales reales registrados: {len(metricas_caudal['caudal_real'])}")

        print("\n[ Monitor de Alarmas ]")
        metricas_alarmas = self.monitor_alarmas.obtener_metricas()
        if not metricas_alarmas['alarmas']:
            print("  No se generaron alarmas durante la simulación.")
        else:
            print(f"  Total de alarmas generadas: {len(metricas_alarmas['alarmas'])}")
            for i, (tiempo, alarma) in enumerate(metricas_alarmas['alarmas']):
                print(f"    {i+1}. Tiempo: {tiempo:.2f}s - Alarma: {alarma}")

        print("\n[ Monitor de Tiempo de Respuesta de Ajuste ]")
        metricas_respuesta = self.monitor_respuesta.obtener_metricas()
        if not metricas_respuesta['tiempos_respuesta']:
            print("  No se completaron ajustes de caudal para medir respuesta.")
        else:
            print(f"  Ajustes de caudal medidos: {len(metricas_respuesta['tiempos_respuesta'])}")
            tiempos = metricas_respuesta['tiempos_respuesta']
            avg_tiempo = sum(tiempos) / len(tiempos)
            print(f"  Tiempo de respuesta promedio: {avg_tiempo:.4f}s")
        
        print("\n[ Monitor del controlador ]")
        metricas_controlador = self.monitor_controlador.obtener_metricas()
        if not metricas_controlador['alarmas']:
            print("  No se detectaron salidas de alarma.")
        else:
            print(f"  Total de alarmas generadas: {len(metricas_controlador['alarmas'])}")
            for i, (tiempo, alarma) in enumerate(metricas_controlador['alarmas']):
                print(f"    {i+1}. Tiempo: {tiempo:.2f}s - Alarma: {alarma}")

        if not metricas_controlador['ajustarCaudal']:
            print("  No se detectaron ajustes de caudal.")
        else:   
            print(f"  Total de ajustes de caudal: {len(metricas_controlador['ajustarCaudal'])}")
            for i, (tiempo, caudal) in enumerate(metricas_controlador['ajustarCaudal']):
                print(f"    {i+1}. Tiempo: {tiempo:.2f}s - Caudal ajustado: {caudal}")

        if not metricas_controlador['ordenApagar']:
            print("  No se detecto apagado en la bomba.")
        else:   
            print(f"  Total ordenes de apagar: {len(metricas_controlador['ordenApagar'])}")
            for i, (tiempo, caudal) in enumerate(metricas_controlador['ordenApagar']):
                print(f"    {i+1}. Tiempo: {tiempo:.2f}s - Caudal ajustado: {caudal}")

        print("\n[ Monitor de la bolsa ]")
        print (f"  Total de alertas de fin de bolsa: {self.monitor_bolsa.obtener_cantidad_de_datos()}")
        print(f"  Tiempo de respuesta promedio desde alerta de fin de bolsa hasta acción del controlador: {self.monitor_bolsa.obtener_tiempo_respuesta_promedio():.4f}s")
        print("-----------------------------\n")

    def graficar_caudal(self, titulo="Simulación"):

        metricas = self.monitor_caudal.obtener_metricas()
        indicado = sorted(metricas['caudal_indicado'], key=lambda p: p[0])
        real      = sorted(metricas['caudal_real'],      key=lambda p: p[0])

        if not indicado and not real:
            print("Sin datos de caudal para graficar.")
            return

        # Caudal indicado como escalón
        t_ind = [p[0] for p in indicado]
        v_ind = [p[1] for p in indicado]

        # Caudal real como línea continua
        t_real = [p[0] for p in real]
        v_real = [p[1] for p in real]

        fig, ax = plt.subplots(figsize=(12, 5))

        ax.step(t_ind, v_ind, where='post',color='#2563eb', linewidth=2, label='Caudal indicado')

        ax.plot(t_real, v_real, color='#dc2626', linewidth=1, linestyle='--', alpha=0.8, label='Caudal real (sensor)')

        # Alarmas como líneas verticales
        metricas_alarmas = self.monitor_alarmas.obtener_metricas()
        colores_alarma = {
            'alarmaBaja':    ('#f59e0b', 'Alarma baja'),
            'alarmaMedia':   ('#f97316', 'Alarma media'),
            'alarmaCritica': ('#dc2626', 'Alarma crítica'),
        }
        alarmas_graficadas = set()
        for t_a, tipo in metricas_alarmas.get('alarmas', []):
            color, etiqueta = colores_alarma.get(tipo, ('#999', tipo))
            label = etiqueta if tipo not in alarmas_graficadas else None
            ax.axvline(x=t_a, color=color, linewidth=1.2,
                    linestyle=':', alpha=0.7, label=label)
            alarmas_graficadas.add(tipo)

        ax.set_xlabel('Tiempo (s)', fontsize=11)
        ax.set_ylabel('Caudal (ml/h)', fontsize=11)
        ax.set_title(f'Caudal indicado vs. caudal real — {titulo}', fontsize=13)
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(left=0)
        ax.set_ylim(bottom=0)

        plt.tight_layout()
        plt.show()

    def graficar_estado_bomba(self, titulo="Simulación"):
        

        metricas = self.monitor_controlador.obtener_metricas()

        # Reunir todos los eventos con su estado resultante
        eventos = []
        for t, _ in metricas['ajustarCaudal']:
            eventos.append((t, 'SIN_ERROR'))
        for t, _ in metricas['ordenApagar']:
            eventos.append((t, 'APAGADO'))
        for t, tipo in metricas['alarmas']:
            if tipo == EstadoBomba.ALARMA_MEDIA:
                eventos.append((t, 'ALARMA_MEDIA'))
            elif tipo == EstadoBomba.ALARMA_CRITICA:
                eventos.append((t, 'APAGADO'))        # crítica → se apaga
            elif tipo == EstadoBomba.ALARMA_BAJA:
                eventos.append((t, 'FIN_BOLSA'))

        if not eventos:
            print("Sin eventos de estado para graficar.")
            return

        eventos.sort(key=lambda e: e[0])

        # Mapa de estados a valores numéricos (eje Y)
        ESTADOS = {
            'SIN_ERROR':    4,
            'ALARMA_MEDIA': 3,
            'FIN_BOLSA':    2,
            'APAGADO':      1,
        }
        COLORES = {
            'SIN_ERROR':    '#22c55e',
            'ALARMA_MEDIA': '#f97316',
            'FIN_BOLSA':    '#f59e0b',
            'APAGADO':      '#dc2626',
        }
        ETIQUETAS = {
            'SIN_ERROR':    'Sin error',
            'ALARMA_MEDIA': 'Alarma media',
            'FIN_BOLSA':    'Fin de bolsa',
            'APAGADO':      'Apagado / Alarma crítica',
        }

        fig, ax = plt.subplots(figsize=(12, 4))

        t_fin = self.tiempoSimulacion

        for i, (t, estado) in enumerate(eventos):
            t_siguiente = eventos[i + 1][0] if i + 1 < len(eventos) else t_fin
            y = ESTADOS[estado]
            ax.fill_between([t, t_siguiente], [y - 0.4, y - 0.4], [y + 0.4, y + 0.4],
                            color=COLORES[estado], alpha=0.35)
            ax.hlines(y, t, t_siguiente,
                    colors=COLORES[estado], linewidth=3)

        # Leyenda manual
        from matplotlib.lines import Line2D
        leyenda = [
            Line2D([0], [0], color=COLORES[e], linewidth=3, label=ETIQUETAS[e])
            for e in ESTADOS
        ]
        ax.legend(handles=leyenda, loc='upper right', fontsize=9)

        ax.set_yticks(list(ESTADOS.values()))
        ax.set_yticklabels([ETIQUETAS[e] for e in ESTADOS], fontsize=10)
        ax.set_xlabel('Tiempo (s)', fontsize=11)
        ax.set_title(f'Estado de la bomba — {titulo}', fontsize=13)
        ax.set_xlim(0, t_fin)
        ax.set_ylim(0.4, 4.6)
        ax.grid(axis='x', alpha=0.3)

        plt.tight_layout()
        plt.show()

    def contar_detenciones_preventivas(self):
        metricas = self.monitor_controlador.obtener_metricas()
        
        # Tiempos en que hubo alarma (baja o crítica)
        t_alarmas = {t for t, tipo in metricas['alarmas'] 
                    #if tipo in {EstadoBomba.ALARMA_BAJA, EstadoBomba.ALARMA_CRITICA}}
                    if tipo in {EstadoBomba.ALARMA_CRITICA}}
        
        count = 0
        for t_apagado, _ in metricas['ordenApagar']:
            # Si se agrega lo de alarmaBaja, deberia comprobar si 65 segundos anteriores hubo una alarma, es preventiva
            if any(t_apagado - 10 <= t_a <= t_apagado for t_a in t_alarmas):
                count += 1
        print(f"Total de detenciones preventivas detectadas: {count}")
        return count


  