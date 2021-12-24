import os
import motor.motor_asyncio
import logging
from typing import List
import datetime

logger = logging.getLogger(__name__)

URI = os.getenv('URI')
DATABASE = os.getenv('DATABASE')
# Establecer conexión con la base de datos

try:
    client = motor.motor_asyncio.AsyncIOMotorClient(URI)
    db = client[DATABASE]
except Exception as e:
    logger.error("No se ha podido establecer la conexión con la base de datos: {}".format(e))
    db = None


class DAO:
    """
    Interfaz a la base de datos
    """
    def __init__(self, db) -> None:
        self.db = db
    

    async def get_range_aggregated(self, client_id: str, from_: datetime.datetime, to_: datetime.datetime) -> dict:
        """
        Devuele un agregado de todos los campos para el rango especificado de tiempo.
        """
        logger.info(f"get_range_aggregated invocada con parámetros: client_id -> {client_id}, from_ -> {from_}, to_ -> {to_}")
        fields = {"power": '$avg', "maximeter": "$sum",
        "reactivePower": "$avg",
        "powerFactor": "$avg",
        "energy": "$sum",
        "reactiveEnergy": "$sum",
        "intensity": "$avg", 
        "voltage": "$avg"} # Mover esto a un archivo config

        from_datetime = datetime.datetime(from_.year, from_.month, from_.day)
        to_datetime = datetime.datetime(to_.year, to_.month, to_.day)
        # Hace esta agregación dinámica, dependiendo del número de campos especificados en "fields"
        agg_aux_fields = {}
        final_projection = {'_id': 0, 'range': {'from': from_datetime, 'to': to_datetime}}
        for field, operation in fields.items():
            agg_aux_fields.update({f"{field}RangeAggregated": {operation: f'${field}.value'},
                f"{field}Unit": {"$first": f'${field}.unit'}})
            final_projection.update({f'{field}': {'aggregatedValue': f'${field}RangeAggregated', 'operation': operation[1:], 'unit': f'${field}Unit'}})
        aggregation_pipeline = [
                {'$match': {'metadata.clientId': client_id, 
                            'timestamp': {'$gte': from_datetime,
                             '$lt': to_datetime + datetime.timedelta(days=1)}}},
                {'$project': {'_id': 0, 'timestamp': 0, 'metadata': 0}},
                {'$group': {'_id': None, **agg_aux_fields}},
                {'$project': final_projection}
           ]
        logger.info(f"Pipeline de agregación conformada: {aggregation_pipeline}")
        try:
            result = await self.db.energyData.aggregate(aggregation_pipeline).to_list(length=None)
            logger.info(f"Datos recibidos: {result}")
            return result[0] if result else {}
        except Exception as e:
            logger.error("Se ha producido un error al obtener los datos: {}".format(e))


    async def get_day_aggregated(self, client_id: str, from_: datetime.datetime, to_: datetime.datetime, field: str) -> List[dict]:
        """
        Devuelve un agregado a nivel diario del rango especificado de tiempo para el campo especificado en field.
        """
        logger.info(f"get_day_aggregated invocada con parámetros: client_id -> {client_id}, from_ -> {from_}, to_ -> {to_}, field -> {field}")
        aggregation_pipeline = [
                {'$match': {'metadata.clientId': client_id, 
                            'timestamp': {'$gte': datetime.datetime(from_.year, from_.month, from_.day),
                             '$lt': datetime.datetime(to_.year, to_.month, to_.day) + datetime.timedelta(days=1)}}},
                {'$project': {'date': {'$dateToParts': {'date': '$timestamp'}}, 'value': f'${field}.value', 'unit': f'${field}.unit'}},
                {'$group': {'_id': {'date': {'year': '$date.year', 'month': '$date.month', 'day': '$date.day'}}, 'aggregated': {'$sum': '$value'}, 'unit': {'$first': '$unit'}}},
                {'$project': {'_id': 0, 'date': {'$dateFromParts': {'year': '$_id.date.year', 'month': '$_id.date.month', 'day': '$_id.date.day'}}, f'{field}Aggregated': '$aggregated', 'unit': '$unit'}},
                {'$sort': {'date': -1}}
           ]
        logger.info(f"Pipeline de agregación conformada: {aggregation_pipeline}")
        try:
            result = await self.db.energyData.aggregate(aggregation_pipeline).to_list(length=None)
            logger.info(f"Datos recibidos: {result}")
            return result
        except Exception as e:
            logger.error("Se ha producido un error al obtener los datos: {}".format(e))

    async def get_range_data(self, client_id: str, from_: datetime.datetime, to_: datetime.datetime, field: str) -> List[dict]:
        """
        Devuelve los datos para un field especificado y en un rango temporal dado con la granularidad temporal máxima.
        """
        logger.info(f"get_range_data invocada con parámetros: client_id -> {client_id}, from_ -> {from_}, to_ -> {to_}, field -> {field}")
        aggregation_pipeline = [
                {'$match': {'metadata.clientId': client_id, 
                            'timestamp': {'$gte': datetime.datetime(from_.year, from_.month, from_.day),
                             '$lt': datetime.datetime(to_.year, to_.month, to_.day) + datetime.timedelta(days=1)}}},
                {'$project': {'_id': 0, 'timestamp': {'$dateToString': {'date': '$timestamp'}}, 'value': f'${field}.value', 'unit': f'${field}.unit'}}
            ]
        logger.info(f"Pipeline de agregación conformada: {aggregation_pipeline}")
        try:
            result = await self.db.energyData.aggregate(aggregation_pipeline).to_list(length=None)
            logger.info(f"Datos recibidos: {result}")
            return result
        except Exception as e:
            logger.error(f"Se ha producido un error al obtener los datos: {e}")
    
    async def get_timestamp_data(self, client_id: str, timestamp: datetime.datetime, field: str = None) -> dict:
        """
        Devuelve un record para el valor más cercano de timpo dada la granuralidad del sistema. Si no se especifica un campo (field) devuelve el record con todos los campos para ese tiempo.
        """
        logger.info(f"get_time_stamp invocada con parámetros: client_id -> {client_id}, timestamp -> {timestamp}, field -> {field}")
        if field:
            projection = {'timestamp': 1, f'{field}': 1}
        else:
            projection = {'_id': 0}
        logger.info(f"Proyección usada: {projection}")

        # Adaptamos el timestamp recibido al timestamp más cercano dada la granularidad por 15 min del diseño de datos del sistema,
        # por ejemplo si se nos envía 2019-10-01T00:17:00 buscaríamos -> 2019-10-01T00:15:00
        closest_minute = round(timestamp.minute / 15 ) * 15
        new_timestamp = datetime.datetime(timestamp.year, timestamp.month, timestamp.day, timestamp.hour, closest_minute)

        try:
            result = await self.db.energyData.find_one({'metadata.clientId': client_id, 'timestamp': new_timestamp}, projection=projection)
            if '_id' in result:
                del result['_id']
            logger.info(f"Datos recibidos: {result}")
            return result
        except Exception as e:
            logger.error(f"Se ha producido un error al obtener los datos: {e}")

    def __bool__(self):
        if self.db:
            return True
        else:
            return False

dao = DAO(db)