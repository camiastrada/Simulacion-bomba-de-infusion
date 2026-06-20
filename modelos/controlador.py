from xdevs.models import Atomic, Port, INFINITY
from lib import EstadoBomba, error_caudal, AccionBomba, CAUDAL_MAX, CAUDAL_MIN, verificar_rango_caudal
import random



#Controlador de bomba de infusión

class Controlador(Atomic):
    def __init__(self, name="controlador"):
        super().__init__(name)
        self.i_orden_medica = Port(float, "ordenMedica")
        self.i_caudal_real = Port(float, "sensorReal")
        self.i_fin_bolsa = Port(bool, "finBolsa")
        self.i_confirmacion = Port(bool, "confirmacionEnfermero")
        self.o_mensaje_actuador = Port(object, "mensajeActuador")
        self.o_alarma = Port(EstadoBomba, "alarma")
        #Puerto de entrada
        self.add_in_port(self.i_orden_medica)
        self.add_in_port(self.i_caudal_real)
        self.add_in_port(self.i_fin_bolsa)  
        self.add_in_port(self.i_confirmacion)
        #Puerto de salida
        self.add_out_port(self.o_mensaje_actuador)
        self.add_out_port(self.o_alarma)


        self.delay = lambda: random.uniform(0.1, 3)
    
    #Estado del controlador(caudal_indicado, sigma_orden, ultima_medicion, estado_bomba, sigma_bomba)
    def initialize(self):    
        self.caudal_indicado = 0.0
        self.sigma_orden = INFINITY
        self.ultima_medicion = 0.0
        self.estado_bomba = EstadoBomba.SIN_ERROR
        self.sigma_bomba = INFINITY
        self.hold_in("pasivo", INFINITY)

    def exit(self): pass

    def _sig(self):
        return min(self.sigma_orden, self.sigma_bomba)
    
    def lambdaf(self):
        #Salida porque expira sigma_orden
        if self.sigma_orden < self.sigma_bomba:
            if(self.caudal_indicado == 0.0):
                #Ingresa caudal cero, y hay que detener la bomba
                self.o_mensaje_actuador.add(AccionBomba.DETENER_BOMBA)
            else:
                #Ingresa caudal distinto a cero, y hay que ajustar caudal
                self.o_mensaje_actuador.add(self.caudal_indicado)
        #Salida porque expira sigma_bomba
        else:
            #Hay error en el caudal, y debo lanzar una alarma media
            if(self.estado_bomba == EstadoBomba.ERROR_CAUDAL):
                self.o_alarma.add(EstadoBomba.ALARMA_MEDIA)
            #Hay fin de bolsa, y debo lanzar una alarma baja
            elif(self.estado_bomba) == EstadoBomba.ALARMA_BAJA:
                self.o_alarma.add(EstadoBomba.ALARMA_BAJA)
            #Ya se lanzó alarma media, hay repetición de error, y debo lanzar una alarma crítica
            elif(self.estado_bomba) == EstadoBomba.ALARMA_MEDIA:
                self.o_alarma.add(EstadoBomba.ALARMA_CRITICA)
    
    def deltint(self):
        #Salida porque expira sigma_orden
        if self.sigma_orden < self.sigma_bomba:
            if(self.estado_bomba == EstadoBomba.ALARMA_CRITICA):
                #Se apago la bomba por una alarma critica, el estado permanece en alarma critica por tiempo indefinido
                self.sigma_orden = INFINITY
            if(self.caudal_indicado == 0.0):
                #Ingresa caudal cero, y hay que detener la bomba
                self.sigma_orden = INFINITY
                self.estado_bomba = EstadoBomba.APAGADO
                self.sigma_bomba = 0.0
            else:
                #Ingresa caudal distinto a cero, mantiene el caudal y actualiza sigma
                self.sigma_bomba -= self.sigma_orden
                self.sigma_orden = INFINITY
        #Salida porque expira sigma_bomba
        else:
            #Hay error en el caudal, paso a alarma media, y actualizo sigma - alarmaMedia dura 5 segundos
            if(self.estado_bomba == EstadoBomba.ERROR_CAUDAL):
                self.sigma_orden -= self.sigma_bomba
                self.estado_bomba = EstadoBomba.ALARMA_MEDIA
                self.sigma_bomba = 5.0
            #Hay fin de bolsa, y se va a apagar en 60 segundos
            elif(self.estado_bomba) == EstadoBomba.ALARMA_BAJA:
                self.caudal_indicado = 0.0
                self.sigma_orden = 60
                self.estado_bomba = EstadoBomba.APAGADO
                self.sigma_bomba = INFINITY
            #Hay que apagar bomba
            elif(self.estado_bomba) == EstadoBomba.APAGADO:
                self.caudal_indicado = 0.0
                self.sigma_orden = INFINITY
                self.estado_bomba = EstadoBomba.SIN_ERROR
                self.sigma_bomba = INFINITY
            #Pasa a estado de alarma crítica, y en 0 seg hay que enviar el mensaje de apagar bomba al actuador
            elif(self.estado_bomba) == EstadoBomba.ALARMA_MEDIA:
                self.caudal_indicado = 0.0
                self.sigma_orden = 0
                self.estado_bomba = EstadoBomba.ALARMA_CRITICA
                self.sigma_bomba = INFINITY

        self.hold_in("activo", self._sig())

    def deltext(self, e):  
        
       
        if not self.i_orden_medica.empty():
            x = self.i_orden_medica.get()
            if x == self.caudal_indicado:
                #Si el caudal indicado es igual al actual, no hay cambio
                self.sigma_orden -= e
                self.sigma_bomba -= e
            elif x == 0.0:
                #Si el caudal indicado es cero, hay que detener la bomba
                self.caudal_indicado = 0.0
                self.sigma_orden = 0.0
                self.sigma_bomba -= e
            elif x > 0.0:
                if (not(verificar_rango_caudal(x))):
                    #Si el caudal indicado es mayor al máximo o menor al mínimo, se considera un error y se rechaza la orden
                    print("Orden médica de caudal fuera de rango, se rechaza la orden")
                    self.sigma_orden -= e
                    self.sigma_bomba -= e
                else:
                    #Si el caudal indicado es distinto de cero, hay que ajustar el caudal
                    self.caudal_indicado = x
                    self.sigma_orden = self.delay()
                    #Si el caudal no causa error, y antes tenia error, pasa a estas sin error
                    #Si el caudal no causa error, y antes no tenia error, se mantiene sin error
                    if (self.estado_bomba in {EstadoBomba.SIN_ERROR, EstadoBomba.ALARMA_MEDIA, EstadoBomba.ALARMA_CRITICA, EstadoBomba.ERROR_CAUDAL} and (not error_caudal(x, self.ultima_medicion))):
                        self.estado_bomba = EstadoBomba.SIN_ERROR 
                        self.sigma_bomba = INFINITY
                    #la nueva indicacion cuasa error, y antes no tenia error, pasa a error de caudal
                    elif (self.estado_bomba in {EstadoBomba.SIN_ERROR} and error_caudal(x, self.ultima_medicion)):
                        self.estado_bomba = EstadoBomba.ERROR_CAUDAL
                        self.sigma_bomba = 5 + self.delay()
                    #la nueva indicacion cuasa error, y antes ya tenia error, se mantiene en error de caudal
                    elif (self.estado_bomba in {EstadoBomba.ALARMA_MEDIA, EstadoBomba.ALARMA_CRITICA, EstadoBomba.ERROR_CAUDAL} and (error_caudal(x, self.ultima_medicion))):
                        self.sigma_bomba -= e
                    #Es estado esta en alarma baja, se mantiene en alarma baja
                    elif (self.estado_bomba in {EstadoBomba.ALARMA_BAJA}):
                        self.sigma_bomba -= e
            
        #Entrada de una nueva medicion de caudal
        elif not self.i_caudal_real.empty():
            #Actualiza la ultima medicion del sensor
            x = self.i_caudal_real.get()
            self.ultima_medicion = x
            self.sigma_orden -= e
            #Si el caudal medido no causa error, y antes tenia error, pasa a estas sin error
            #Si el caudal medido no causa error, y antes no tenia error, se mantiene sin error
            if (self.estado_bomba in {EstadoBomba.SIN_ERROR, EstadoBomba.ALARMA_MEDIA, EstadoBomba.ALARMA_CRITICA, EstadoBomba.ERROR_CAUDAL} and (not error_caudal(self.caudal_indicado, x))):
                self.estado_bomba = EstadoBomba.SIN_ERROR 
                self.sigma_bomba = INFINITY
            #la nueva medicion cuasa error, y antes no tenia error, pasa a error de caudal
            elif(self.estado_bomba in {EstadoBomba.SIN_ERROR} and error_caudal(self.caudal_indicado, x)):
                self.estado_bomba = EstadoBomba.ERROR_CAUDAL
                self.sigma_bomba = 5
            #la nueva medicion cuasa error, y antes ya tenia error, se mantiene en error de caudal
            elif(self.estado_bomba in {EstadoBomba.ALARMA_MEDIA, EstadoBomba.ALARMA_CRITICA, EstadoBomba.ERROR_CAUDAL} and (error_caudal(self.caudal_indicado, x))):
                self.sigma_bomba -= e
            #Es estado esta en alarma baja, se mantiene en alarma baja
            elif(self.estado_bomba in {EstadoBomba.ALARMA_BAJA}):
                self.sigma_bomba -= e

        #Entrada de fin de bolsa
        if not self.i_fin_bolsa.empty():
            fin_bolsa = self.i_fin_bolsa.get()
            if fin_bolsa:
                #Si hay fin de bolsa, hay que lanzar alarma baja
                self.sigma_orden -= e
                self.estado_bomba = EstadoBomba.ALARMA_BAJA
                self.sigma_bomba = 0.0

        #Entrada de confirmación del enfermero
        elif not self.i_confirmacion.empty():
            print("Controlador recibe confirmación del enfermero")
            confirmacion = self.i_confirmacion.get()
            if confirmacion and self.estado_bomba == EstadoBomba.ALARMA_CRITICA:
                #Si se confirma la alarma crítica, se vuelve al estado sin error
                self.sigma_orden -= e
                self.estado_bomba = EstadoBomba.SIN_ERROR
                self.sigma_bomba = INFINITY

        self.hold_in("activo", self._sig())