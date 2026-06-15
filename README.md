# Sistema de Simulación DEVS - Bomba de Infusión Médica

Este proyecto implementa un entorno de simulación de eventos discretos basado en la metodología formal **DEVS (Discrete Event System Specification)**. Modela el comportamiento lógico de una bomba de infusión médica interactuando con su entorno físico (sensores de caudal) y el factor humano (operador/enfermera).

Se utiliza **PythonPDEVS** como motor principal de ejecución.

---

##  Requisitos

* **Python 3.8** o superior.
* **Git** 

---

## Guía de Instalación 
PythonPDEVS Debe instalarse directamente desde su código fuente oficial.

Comandos: 

### 1. Clonar el repositorio del motor de simulación
```bash
git clone https://github.com/capocchi/PythonPDEVS
```

### 2. Instalar la librería en tu entorno de Python
Accede al directorio de fuentes (`src`) del repositorio descargado y ejecuta el script de instalación:
```bash
cd PythonPDEVS/src
python setup.py install --user
```
*(Nota: El parámetro `--user` garantiza la instalación local en tu usuario actual, evitando la necesidad de permisos de administrador o comandos `sudo`).*

### 3. Verificar que la instalación fue exitosa
Vuelve a la raíz de tu terminal y ejecuta la siguiente línea de comandos. Si devuelve el mensaje de éxito, la suite está lista para usarse:
```bash
python -c "from pypdevs.DEVS import AtomicDEVS, CoupledDEVS; print('PythonPDEVS se instaló correctamente')"
```


##  Ejecución de la Simulación

Desde la carpeta raíz del proyecto, ejecutá:

```bash
python main.py
```

