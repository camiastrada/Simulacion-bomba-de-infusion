from sistema import SistemaInfusionAcoplado
from xdevs.sim import Coordinator
from monitores.monitor_caudal import MonitorCaudal
from monitores.monitor_alarmas import MonitorAlarmas
from monitores.monitor_actualizacion_caudal import MonitorRespuesta
from monitores.monitor_controlador import MonitorControlador
from lib import CAUDAL_MAX
from simulacion.simulacion import Simulacion
import random


# Escenario 1: Funcionamiento normal sin fallas
def escenario1():
     print("Escenario 1: Funcionamiento normal sin fallas")
     simular = Simulacion("SimulacionBombaInfusion")
     simular.iniciar_simulacion(10800.0,None,None,None,None)
     simular.mostrar_metricas()
     simular.graficar_timeline("Escenario 1: Funcionamiento normal sin fallas")
     simular.graficar_caudal("Escenario 1: Funcionamiento normal sin fallas") 
     simular.graficar_estado_bomba("Bomba: Funcionamiento normal sin fallas")
     simular.contar_detenciones_preventivas()

# Escenario 2: Cambia orden medica durante la infusion
# el generador emite una orden de 50, y a los 2 segundo emite orden de 80... luego no deberia emitir nada por 10000 segundos
def escenario2():
     print("Escenario 2: Cambia orden medica durante la infusión")
     valores_f = iter([50.0, 80.0])
     def f():
          return next(valores_f, 80.0) # después sigue devolviendo 80

     valores_g = iter([1.0, 2.0, 10000.0])
     def g():
          return next(valores_g, 3000)
     simular = Simulacion("SimulacionBombaInfusion")
     simular.iniciar_simulacion(10800.0,f,g,None,None)
     simular.mostrar_metricas()
     simular.graficar_timeline( "Escenario 2: Cambia orden medica durante la infusión")
     simular.graficar_caudal("Escenario 2: Cambia orden medica durante la infusión") 
     simular.graficar_estado_bomba("Bomba: Cambia orden medica durante la infusión")
     simular.contar_detenciones_preventivas()

# Escenario 3 se genera orden 0.0
def escenario3():
     print("Escenario 3: Se genera orden 0.0")
     def f():
          if random.random() < 0.15:  # 15% de probabilidad de que salga 0
               return 0.0
          return random.uniform(0.0, 200.0)
     simular = Simulacion("SimulacionBombaInfusion")
     simular.iniciar_simulacion(10800.0,f,None)
     simular.mostrar_metricas()  
     simular.graficar_timeline( "Escenario 3: Se genera orden 0.0")
     simular.graficar_caudal("Escenario 3: Se genera orden 0.0") 
     simular.graficar_estado_bomba("Bomba escenario 3: Se genera orden 0.0")
     simular.contar_detenciones_preventivas()


#Error de caudal

def funcion_con_error(n_errores=4, inicio_minimo=5, inicio_maximo=15):
     
     inicio = [random.randint(inicio_minimo, inicio_maximo)]
     contador = [0]
     errores_dados = [0]
     def fun(x):
          if x > 0:
               contador[0] += 1
               if contador[0] >= inicio[0] and errores_dados[0] < n_errores:
                    errores_dados[0] += 1
                    if errores_dados[0] == n_errores:
                         # Resetea todo para el próximo ciclo
                         contador[0] = 0
                         errores_dados[0] = 0
                         inicio[0] = random.randint(inicio_minimo, inicio_maximo)
                    return random.uniform(x * 0.5, x * 0.7)
               return random.uniform(x * 0.97, x * 1.03)
          return x
     return fun


# Escenarip 4: Por momentos el caudal real es distinto al indicado, pero el controlador lo maneja y no salen alarmas
def escenario4():  
     print("Escenario 4: Por momentos el caudal real es distinto al indicado, pero el controlador lo maneja y no salen alarmas")   
     simular = Simulacion("SimulacionBombaInfusion")
     simular.iniciar_simulacion(3600.0,None,None,funcion_con_error(4,120,300),None)
     simular.mostrar_metricas()  
     simular.graficar_timeline( "Escenario 4: Desvío leve de caudal que es corregido por el controlador ")
     simular.graficar_caudal( "Caudal Escenario 4: Desvío leve de caudal que es corregido por el controlador ")
     simular.graficar_estado_bomba( "Bomba Escenario 4: Desvío leve de caudal que es corregido por el controlador ")
     simular.contar_detenciones_preventivas()


# Escenario 5: Por momentos el caudal real es distinto al indicado, el controlador pasa a alarma media, pero no llega a alarma critica


def escenario5_con_alarma_media():  
     print("Escenario 5: Por momentos el caudal real es distinto al indicado, el controlador pasa a alarma media, pero no llega a alarma crítica")   
     simular = Simulacion("SimulacionBombaInfusion")
     simular.iniciar_simulacion(3600.0,None,None,funcion_con_error(7,10,300),None)
     simular.mostrar_metricas()  
     simular.graficar_timeline( "Escenario 5 con Alarma Media. Desvío de caudal mayor al 10 porciento durante más de 5 segundos.")
     simular.graficar_caudal( " Escenario 5 con Alarma Media.  Desvío de caudal mayor al 10 porciento durante más de 5 segundos.")
     simular.graficar_estado_bomba( " Escenario 5 con Alarma Media. Desvío de caudal mayor al 10 porciento durante más de 5 segundos.")
     simular.contar_detenciones_preventivas()

# Escenarip 5: Por momentos el caudal real es distinto al indicado, el controlador pasa a alarma media, y luego llega a alarma critica
def escenario5_con_alarma_critica():
     print("Escenario 5: Por momentos el caudal real es distinto al indicado, el controlador pasa a alarma media, y luego llega a alarma crítica")
     simular = Simulacion("SimulacionBombaInfusion")
     simular.iniciar_simulacion(3600.0,None,None,funcion_con_error(12,120,300),None)
     simular.mostrar_metricas()  
     simular.contar_detenciones_preventivas()
     simular.graficar_timeline( "Escenario 5 con Alarma Crítica. Desvío de caudal mayor al 10 porciento durante más de 5 segundos.")
     simular.graficar_caudal( " Escenario 5 con Alarma Crítica.  Desvío de caudal mayor al 10 porciento durante más de 5 segundos.")
     simular.graficar_estado_bomba( " Escenario 5 con Alarma Crítica. Desvío de caudal mayor al 10 porciento durante más de 5 segundos.")
     


def escenario6(): 
     print("Escenario 6: Fin de bolsa con confirmación del enfermero")
     # Escenario 6: Fin de bolsa con confirmación del enfermero
     # Se fija caudal alto para vaciar la bolsa en un tiempo corto de simulación.
     # El enfermero confirma la alarma baja luego de 20s.
     def funcion_caudal_max():
          return 200.0

     valores_emision = iter([1.0, 60000.0])
     def funcion_emision_orden():
          return next(valores_emision, 3000)


     def t_confirmacion_enfermero():
          return 25.0

     simular = Simulacion("SimulacionBombaInfusion")
     simular.iniciar_simulacion(2000.0, funcion_caudal_max, funcion_emision_orden , None, t_confirmacion_enfermero)
     simular.mostrar_metricas()
     simular.graficar_timeline("Escenario 6: Fin de bolsa con confirmación del enfermero.")
     simular.graficar_caudal(" Escenario 6: Fin de bolsa con confirmación del enfermero.")
     simular.graficar_estado_bomba("Bomba Escenario 6: Fin de bolsa con confirmación del enfermero.")



# Escenario 7: Alarma crítica - sensor mide mal, enfermero confirma tarde
   
def escenario7():
     print("Escenario 7: Alarma crítica - sensor mide mal, enfermero confirma tarde")
     # El sensor mide solo el 50% del caudal real → error de caudal
     def funcion_caudal_escenario7():
               return 2.0
          
     valores_t_emision = iter([1.0, 60000.0])
     def funcion_emision_orden_7():
               return next(valores_t_emision, 3000)


          # Sensor mide solo el 50% del caudal real → error de caudal garantizado
     def funcion_precision_error(x):
               return x * 0.5 
          
          # Enfermero confirma recién a los 90s (después de que escale a crítica)
     def t_confirmacion_tarde():
               return 60.0

     simular = Simulacion("SimulacionBombaInfusion")
     simular.iniciar_simulacion(
               200.0,
               funcion_caudal_escenario7,
               funcion_emision_orden_7   ,
               funcion_precision_error,   #fuerza el error de caudal
               t_confirmacion_tarde
          )
     simular.mostrar_metricas()
     simular.graficar_timeline("Escenario 7: Alarma crítica no confirmada durante 30 segundos.")
     simular.graficar_caudal(" Escenario 7: Alarma crítica no confirmada durante 30 segundos.")
     simular.graficar_estado_bomba("Bomba Escenario 7: Alarma crítica no confirmada durante 30 segundos.")


# Escenario 8: Trato de generar ordenes mayor a caudal maximo (200)
def escenario8():
     print("Escenario 8: Generación ordenes mayor a caudal maximo 200")
     valores_c_emision = iter([600.0,10.0,500.0,300.0, 300.0, 10.0])
     def funcion_emision_orden():
               return next(valores_c_emision, 300.0)

     simular = Simulacion("SimulacionBombaInfusion")
     simular.iniciar_simulacion(36000.0,
            funcion_emision_orden,
            None,None,None)
     simular.mostrar_metricas()
     simular.graficar_caudal("Tratar de generar ordenes mayor a caudal maximo")
    
if __name__ == "__main__":

     #Escenario 1: Funcionamiento normal sin fallas
     # escenario1()

     # #Escenario 2: Cambia orden medica durante la infusion
     # #el generador emite una orden de 50, y a los 2 segundo emite orden de 80... luego no deberia emitir nada por 10000 segundos
     # escenario2()

     # # Escenario 3 se genera orden 0.0
     # escenario3()
     
     # # Escenario 4: Por momentos el caudal real es distinto al indicado, pero el controlador lo maneja y no salen alarmas
     # escenario4()

     # # Escenario 5: Por momentos el caudal real es distinto al indicado, el controlador pasa a alarma media, pero no llega a alarma critica
     # escenario5_con_alarma_media()

     #  Escenario 5: Por momentos el caudal real es distinto al indicado, el controlador pasa a alarma media, y luego llega a alarma critica
     escenario5_con_alarma_critica()

     # # Escenario 6: Fin de bolsa con confirmación del enfermero
     # escenario6() 

     # # Escenario 7: Alarma crítica - sensor mide mal, enfermero confirma tarde
     # escenario7()

     # # Escenario 8: Trato de generar ordenes mayor a caudal maximo (200)
     # escenario8()
