# metricas-github

Este repo tiene scripts que se encargan de entregarnos datos de metricas que
podemos extraer de los repositorios que tiene la organización.

# Disponibles

* pr.py: extrae datos de pull requests y procesa lo PR mergeados

## PR 

Para usar este script se requiere python 3.6 o superior y el módulo `github`.

### Requerimientos

#### Token de github

Es necesario tener un token de github con permisos suficientes para leer datos
de la organizacion, leer datos de los usuarios y leer datos de los repositorios.
Para obtener el token puede usar la documentación de github para crear tokens
de acceso personal.

Una vez tenemos el token generado, debemos exportarlo en una variable de
entorno. Esto es posible usando el comando `export` en la terminal, tambien se
puede hacer esto en el archivo `.bashrc` o `.zshrc` de la terminal
 
El nombre de la variable debe ser `GH_TOKEN`.

#### Python 3.6 o superior
Use el manejador de paquetes preferido segun su OS para instalar python. y el
manejador de paquetes `pip` o `pipenv`.

#### Virtualenv

Este es un paquete de python que permite crear entornos virtuales de python. Es
util para poder tener las dependencios por separado de la instalación global de
python.


### Como iniciar

Puede iniciar por crear un entorno virtual con python 3.6 o superior. Apara esto
se puede usar el paquete `venv` de python. 

```bash

# crear entorno virtual

python -m venv ./.venv
# tambien es posible usar virtualenv directamente en el terminal si esta en nuestro PATH
virtualenv ./.venv

```

Ahora debemos activar el entorno virtual

```bash
source ./.venv/bin/activate

# en casi de que se requiera desactivar el entorno virtual en la misma terminal
# en la que ya esta activo de puede ejecutar el comanfo
deactivate
```

Una vez activado el entorno virtual, se pueden instalar las dependencias con un manejador de paquetes como `pip` o `pipenv`.

```bash
pip install -r requirements.txt
```

Ahora se puede usar el script `pr.py` para extraer datos de pull requests de
repositorios de la organización. el comando para iniciar el script es:

```bash
python pr.py
```

#### Funcionamiento 

Este script genera un archivo `gh.db` en el directorio actual, este archivo
es una base de datos sqlite3 que se usa para almacenar los datos extraidos de
los distinos repositorios de la organizació. Aca se almacenan registros
de los pull requests, esto es util para poder generar reportes basados en
consultas a la base de datos. Tambien genera un archivo de log en elque se puede
seguir el progreso de las operaciones que se realizan y finalmente genera un
archivo de csv con los datos extraidos de los pull requests, que se puede usar
para importarlo en otros sistemas o en un sheet para generar reportes o dashboards.

Actualmente el script trae toda la data de Github y almacena en DB unicamente
los pull requests que no han sido agregados a la base de datos.

#### Uso

El script puede recibir como argumento una fecha de inicio, a partir de la cual
se extraeran los pull requests. Por defecto se extrae desde el ultimo mes.

```bash
python pr.py "2021-01-01"
```

#### Mas adelante

La idea de esto es poder agregar mas scripts para generar metricas utiles para
la organizacion y tambien se puede iterar y mejorar este script para que no
siempre vayamos a extraer la data de Github. 

Se puede agregar mas parametros a este script para poder elegir un rango
especifico de fechas de inicio y fin a consultar y esto con la DB que ya existe
puede hacer que sea mas eficiente, ya qye no se tendria que ir a traer toda la
data de Github cada vez que se ejecute el script.
