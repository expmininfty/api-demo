# Importa los datos, los prepara e inserta en la base de datos
from typing import Tuple
import pandas as pd
from pymongo import MongoClient
import pymongo
import os
import math
uri = os.getenv('URI') or 'localhost' # for testing purposes

client = MongoClient(uri)

data = pd.read_csv('data/monitoring_report.csv', parse_dates={'timestamp': [0]})
data = data.to_dict('records')
# Transforma los datos para adaptación esquema bbdd
def get_name_unit(key_: str) -> Tuple[str, str]:
    """
    Prepara el nombre en formato adecuado para la inserción en base de datos 
    a partir de los nombres de las columnas y extre la unidad de medida.
    """
    first_, last_ = key_.split(' (')
    unit = last_.replace(')', '').strip()
    field_name = ''.join(word.title() for word in map(lambda z: z.strip().lower(), first_.split(' ')))
    field_name = field_name[0].lower() + field_name[1:]
    return field_name, unit

data_out = []
for dat in data:
    record = {'metadata': {'clientId': '1', 'clientName': 'Cliente 1'}}
    record.update({'timestamp': dat['timestamp']})
    del dat['timestamp']
    for key, value in dat.items():
        field_name, unit = get_name_unit(key)
        record.update({field_name: {'unit': unit , 'value': value if not math.isnan(value) else None}})
    data_out.append(record)

# Creación coleccion e inserción en base de datos
db = client['test']
db.drop_collection("energyData") # Eliminar colección si existiera previamente
db.create_collection("energyData", timeseries={'timeField': 'timestamp', 'metaField': 'metadata', 'granularity': 'minutes'})
db['energyData'].insert_many(data_out)
db.energyData.create_index([('timestamp', pymongo.DESCENDING), ('metadata.clientId', pymongo.DESCENDING)]) # Creamos índices sobre compuestos sobre cliente y fecha y por cliente solo para un filtrado más eficiente.
db.energyData.create_index([('metadata.clientId', pymongo.DESCENDING)])