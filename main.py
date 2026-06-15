from sistema import SistemaInfusionAcoplado
from xdevs.sim import Coordinator

if __name__ == "__main__":
    # 1. Crear el sistema acoplado (la maqueta completa)
    sistema = SistemaInfusionAcoplado("Suite_Simulacion_Medica")
    
    # 2. Pasar el sistema al motor de simulación 
    simulador = Coordinator(sistema)

    # 3. Inicializan los componentes
    simulador.initialize()

    # 4. Configurar parámetros de ejecución
    TIEMPO_SIMULACION = 3600.0

    # 5. Arrancar el motor de simulación
    
    print("=========================================")
    print(" INICIANDO SIMULACIÓN DE EVENTOS DISCRETOS")
    print("=========================================")
    

    simulador.sim(3600.0)

    
    print("=========================================")
    print(" SIMULACIÓN FINALIZADA CON ÉXITO")
    print("=========================================")



# utilizar **Recomendado:** `from pypdevs.minimal import Simulator`