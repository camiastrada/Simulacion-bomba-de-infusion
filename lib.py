from enum import Enum
from typing import NewType

# ─────────────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────────────
CAUDAL_MAX = 200.0  # ml/h
CAUDAL_MIN = 0.0    # ml/h
DELAY_ACTUADOR = 0.5  # segundos
CAPACIDAD_BOMBA = 80.0  # ml
PERIODO_MUESTREO_SENSOR = 1.0  # segundos


# ─────────────────────────────────────────────────────────────
# TIPOS
# ─────────────────────────────────────────────────────────────

# Definición de tipos primitivos claros
Caudal = NewType('Caudal', float)
Time = NewType('Time', float)

# Estructuras de Mensajes Simples 
class FinalBolsa:
    def __repr__(self): return "finBolsa"
FIN_BOLSA = FinalBolsa()

class Confirmacion:
    def __repr__(self): return "confirmado"
CONFIRMADO = Confirmacion()

# EstadoBomba 
class EstadoBomba(Enum):
    ERROR_CAUDAL = "errorCaudal"
    ALARMA_BAJA = "alarmaBaja"
    ALARMA_MEDIA = "alarmaMedia"
    ALARMA_CRITICA = "alarmaCritica"
    SIN_ERROR = "sinError"
    APAGADO = "apagado"

#
class AccionBomba(Enum):
    DETENER_BOMBA = "detenerBomba"


# ─────────────────────────────────────────────────────────────
# FUNCIONES DE UTILIDAD
# ─────────────────────────────────────────────────────────────

def verificar_rango_caudal(valor: float) -> bool:
    
    return CAUDAL_MIN <= valor <= CAUDAL_MAX
# Retorna True si el desfase real supera el 10% del valor indicado.
def error_caudal(indicado: float, real: float) -> bool:
   
    if not (verificar_rango_caudal(indicado) and verificar_rango_caudal(real)):
        raise ValueError("Los caudales deben estar en el rango de [0, 200] ml/h")
        
    if abs(indicado - real) > (indicado * 0.1):
        return True
    else:
        return False
