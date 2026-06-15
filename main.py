from pypdevs.simulator import Simulator
from sistema import SistemaInfusion

if __name__ == "__main__":
    # 1. Crear el sistema acoplado (la maqueta completa)
    sistema = SistemaInfusion("Suite_Simulacion_Medica")
    
    # 2. Pasar el sistema al motor de simulación de PythonPDEVS
    simulador = Simulator(sistema)
    
    # 3. Configurar parámetros de ejecución
    # Simularemos 3600 segundos virtuales (1 hora de tiempo simulado)
    simulador.setTerminationTime(3600.0)
    
  
    # para ver únicamente los prints limpios que pusimos en los componentes
    simulador.setVerbose(None)
    
    print("=========================================")
    print(" INICIANDO SIMULACIÓN DE EVENTOS DISCRETOS")
    print("=========================================")
    
    # 4. Arrancar el motor de simulación
    simulador.simulate()
    
    print("=========================================")
    print(" SIMULACIÓN FINALIZADA CON ÉXITO")
    print("=========================================")



# utilizar **Recomendado:** `from pypdevs.minimal import Simulator`