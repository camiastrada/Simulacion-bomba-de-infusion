from xdevs.models import Atomic, Coupled, Port, INFINITY


#
class SensorFlujo(Atomic):
    def __init__(self, name="actuador"):
        super().__init__(name)