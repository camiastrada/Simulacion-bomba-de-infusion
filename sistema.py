from pypdevs.DEVS import CoupledDEVS
from modelos.generador_ordenes import GeneradorOrdenes
class SistemaInfusionAcoplado(CoupledDEVS):
    """
    Representa la red o 'suite' completa del sistema de infusión.
    Conecta el entorno físico, el factor humano y el software de la bomba.
    """
    def __init__(self, nombre):
        super().__init__(nombre)
        
        # 1. INSTANCIAR TODOS LOS COMPONENTES 
        self.generador_ordenes = self.addSubModel(GeneradorOrdenes("Generador_Ordenes"))
      
        self.bomba = self.addSubModel(ControladorBombaInfusion("Bomba_Medica"))
        
        # 2. ACOPLAMIENTO DE PUERTOS (El "Cableado" del Sistema)
        
        #ejemplo: ordenes médicas entran a la bomba
        self.connectPorts(self.generador_ordenes.ordenMedica, self.bomba.entrada_orden)
        
