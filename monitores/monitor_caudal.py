class MonitorCaudal:
    def __init__(self):
        self.caudal_indicado = []
        self.caudal_real = []

    def observar_orden(self, t, valor):
        self.caudal_indicado.append((t, valor))

    def observar_flujo(self, t, valor):
        self.caudal_real.append((t, valor))

    def calcular_tiempo_infusion_correcta(self, tiempo_total: float, tolerancia: float = 0.1) -> float:
        
        if not self.caudal_indicado or not self.caudal_real:
            return 0.0

        # Construir lista de (t, valor) para caudal indicado como escalón
        indicado = sorted(self.caudal_indicado, key=lambda p: p[0])
        real      = sorted(self.caudal_real,     key=lambda p: p[0])

        # Todos los puntos de cambio
        tiempos = sorted(set(t for t, _ in indicado) | set(t for t, _ in real))
        tiempos.append(tiempo_total)

        def valor_en(serie, t):
            """Último valor de la serie escalonada antes o en t"""
            v = None
            for ts, vs in serie:
                if ts <= t:
                    v = vs
                else:
                    break
            return v

        tiempo_correcto = 0.0

        for i in range(len(tiempos) - 1):
            t_ini = tiempos[i]
            t_fin = tiempos[i + 1]
            dt = t_fin - t_ini

            v_ind = valor_en(indicado, t_ini)
            v_real = valor_en(real, t_ini)

            if v_ind is None or v_real is None or v_ind == 0:
                continue

            error = abs(v_real - v_ind) / v_ind
            if error <= tolerancia:
                tiempo_correcto += dt

        return (tiempo_correcto / tiempo_total) * 100.0
    def obtener_metricas(self):
        return {
            "caudal_indicado": self.caudal_indicado,
            "caudal_real": self.caudal_real
        }

    

