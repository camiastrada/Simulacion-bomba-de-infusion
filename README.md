# Sistema de Simulación DEVS - Bomba de Infusión Médica
Este proyecto implementa un entorno de simulación de eventos discretos basado en la metodología formal DEVS utilizando el motor xDEVS. El sistema modela el comportamiento lógico de una bomba de infusión médica, interactuando con su entorno físico (sensores de caudal) y el factor humano (operador/enfermero).

## Visualización de Resultados
El sístema  simula 7 casos del sístema detallados en el informe uno a uno.
Al simular un caso se registran datos de la simulación, se generan gráficos y métricas en consola. Al cerrar las ventanas de gráficos la ejecución continua con el caso siguiente.

### Métricas en consola: 
- Resumen detallado de detenciones preventivas
- Registro de alarmas generadas
- tiempos de respuesta de cambios de caudal o reacción ante fin de bolsa.

### Gráficos: 
- Caudal indicado vs. caudal real (sensor) 
- Timeline de eventos (alarmas, fin de bolsa, acciones del enfermero)
- Historial de estados de la bomba a lo largo del tiempo.


## Requisitos 
- Python 3.10+
- xdevs
- matplotlib

## Guía de Instalación
1. Clonar el repositorio del proyecto:

Bash
git clone https://github.com/camiastrada/Simulacion-bomba-de-infusion

2. Instalar el motor xDEVS en tu entorno de Python:

Bash
pip install xdevs

3. Verificar la instalación:

Bash
python -c "import xdevs; print('xDEVS se instaló correctamente')"

4. Ejecutar el Proyecto
Desde la carpeta raíz del proyecto (donde se encuentra el archivo main.py) se ejecuta:

Bash
python main.py


## Estructura del Repositorio
/simulacion: Contiene la lógica central del modelo DEVS y los monitores de eventos.

/monitores: Clases especializadas en el registro de métricas temporales y estados.

/lib: Definición de clases auxiliares, Enums de estados de la bomba y acciones del controlador.

main.py: Punto de entrada principal para configurar y ejecutar los distintos escenarios de prueba.
