# api-demo
API Demo

### Descripción
Proyecto de prueba de una API para el consumo de una interfaz gráfica. Construido con FastAPI y MongoDB con soporte asíncrono mediante `moto`.

Para ejecutar el proyecto se necesita disponer de una instalación de python con una versión 3.8+ y mongoDB 5+ para la explotación del uso de las series temporales.

### Instalación
* Crear un entorno virtual e instalar las dependencias sobre el directorio del repo
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip3 install -r requirements.txt
    ```
* Setear las variables de entorno para la conexión a la base de datos <br/>
    ``` bash
    export URI=tuuri DATABASE=tubasededatos
    ```
* Ejecutar `setup.py` para preparar los datos e insertarlos en la base de datos.
    ``` bash
    python3 setup.py
    ```
* Ejecutar la aplicación usando uvicorn, el servidor asíncrono comunmente usado con FastAPI
    ``` bash
    uvicorn app.main:app
    ```

### Uso
Ir a alguno de los _end points_ habilitados (todos los endpoints necesitan un identificador del cliente concreto, en este caso hemos usado `1` como prueba). El detalle de los parámetros y pares clave valor se puede encontrar en la documentación asociada de Swagger en `.../docs`:
* `.../range-detail/{field}` devuelve para un campo específico el detalle máximo de granularidad temporal incluído en un rango temporal. <br/>
    Ejemplo: <br/>
    `http://127.0.0.1:8000/range-detail/power?clientId=1&from_=2019-10-09&to_=2019-10-15`
    ```json
    [
  {
    "timestamp": "2019-10-15T00:00:00.000Z",
    "value": 18.488,
    "unit": "kW"
  },
  {
    "timestamp": "2019-10-15T00:15:00.000Z",
    "value": 17.565,
    "unit": "kW"
  },
  {
    "timestamp": "2019-10-15T00:30:00.000Z",
    "value": 16.928,
    "unit": "kW"
  },
  {
      "goesOn": "the data goes on..."
  }
  ]
    ```
* `.../day-aggregated/{field}` devuelve para un campo específico el detalle agregado por día dentro de un rango especificado. <br/>
    Ejemplo: <br/>
    `http://127.0.0.1:8000/day-aggregated/power?clientId=1&from_=2019-10-09&to_=2019-10-15`
    ```json
    [
  {
    "date": "2019-10-15T00:00:00",
    "powerAggregated": 1481.227,
    "unit": "kW"
  },
  {
    "date": "2019-10-14T00:00:00",
    "powerAggregated": 1536.925,
    "unit": "kW"
  },
  {
    "date": "2019-10-13T00:00:00",
    "powerAggregated": 1564.509,
    "unit": "kW"
  },
  {
    "date": "2019-10-12T00:00:00",
    "powerAggregated": 1929.243,
    "unit": "kW"
  },
  {
    "date": "2019-10-11T00:00:00",
    "powerAggregated": 2032.552,
    "unit": "kW"
  },
  {
    "date": "2019-10-10T00:00:00",
    "powerAggregated": 882.521,
    "unit": "kW"
  },
  {
    "date": "2019-10-09T00:00:00",
    "powerAggregated": 486.079,
    "unit": "kW"
  }
  ]
    ```
* `.../range-aggregated` agrega para un rango de tiempo especificado todos los campos disponibles utilizando una función dada (suma, media, etc.) Esto puede servir para un resumen general en el cuadro de mandos. <br/>
    Ejemplo: <br/>
    `http://127.0.0.1:8000/range-aggregated/?clientId=1&from_=2019-10-09&to_=2019-10-15`

    ```json
    {
  "range": {
    "from": "2019-10-09T00:00:00",
    "to": "2019-10-15T00:00:00"
  },
  "power": {
    "aggregatedValue": 14.90685112781955,
    "operation": "avg",
    "unit": "kW"
  },
  "maximeter": {
    "aggregatedValue": 10366.972,
    "operation": "sum",
    "unit": "kW"
  },
  "reactivePower": {
    "aggregatedValue": -5.045674277016743,
    "operation": "avg",
    "unit": "kVAr"
  },
  "powerFactor": {
    "aggregatedValue": 0.8632947368421052,
    "operation": "avg",
    "unit": "φ"
  },
  "energy": {
    "aggregatedValue": 3229.891,
    "operation": "sum",
    "unit": "kWh"
  },
  "reactiveEnergy": {
    "aggregatedValue": 245.71,
    "operation": "sum",
    "unit": "kVArh"
  },
  "intensity": {
    "aggregatedValue": 80.17746879756469,
    "operation": "avg",
    "unit": "A"
  },
  "voltage": {
    "aggregatedValue": 178.5928045112782,
    "operation": "avg",
    "unit": "V"
  }
    }
    ```
* `.../timestamp`  Devuelve para un punto temporal, el registro más cercano dada la granularidad del sistema, si se especifica un campo concreto (field) se realizará una proyección para devolver sólo la información de este, en caso contraro se devuelven todos los campos del registro. <br/>
  Ejemplo: <br/>
  `http://127.0.0.1:8000/timestamp?clientId=1&timestamp=2019-10-09T00:00:00`

  ```json
  {
  "timestamp": "2019-10-09T00:00:00",
  "metadata": {
    "clientId": "1",
    "clientName": "Cliente 1"
  },
  "intensity": {
    "unit": "A",
    "value": 15.508
  },
  "maximeter": {
    "unit": "kW",
    "value": 3.185
  },
  "power": {
    "unit": "kW",
    "value": 3.131
  },
  "reactivePower": {
    "unit": "kVAr",
    "value": 2.192
  },
  "powerFactor": {
    "unit": "φ",
    "value": 0.878
  },
  "voltage": {
    "unit": "V",
    "value": 244.74
  },
  "energy": {
    "unit": "kWh",
    "value": 0.7
  },
  "reactiveEnergy": {
    "unit": "kVArh",
    "value": 0.5
  }
  }
  ```

### Comentarios y mejoras
Se decide utilizar un framework, FastAPI, con capacidad asíncrona para poder cargar de manera no bloqueante las distintas tablas de la interfaz. Se decide utilizar mongoDB 5+ por su capacidad para tratar con series temporales, lo cual permite realizar agregaciones en ventanas temporales y devolver los datos en un formato muy amigable para el intercambio de información web, por ser muy cercano a JSON.

Como mejora se podrían dockerizar las aplicaciones, implementar un sistema de caching con `Redis` y autenticación mediante `oauth2`. Diseñar una buena batería de test unitarios usando `pytest`. Mejorar el manejo de excepciones, generando nuevas con un significado más concreto, detallar el logging para una mejor experiencia en el debugging y crear modelos pydantic de respuesta API, así se complementaría también la documentación autogenerada por FastAPI.
