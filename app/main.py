import datetime
from fastapi import FastAPI, HTTPException
from .dao import dao
from .models import allowedFields
from datetime import date
from typing import Optional

app = FastAPI()


@app.get('/range-detail/{field}')
async def get_field_daily_detail(field: allowedFields, clientId: str, from_: date, to_: date):
    """
    Devuelve el detalle granual temporal del campo especificado en el path. Serviría para representar los gráficos con detalle diario.
    """
    if dao:
        result = await dao.get_range_data(clientId, from_, to_, field)
        return result
    else:
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@app.get('/day-aggregated/{field}')
async def get_day_aggregated(field: allowedFields, clientId: str, from_: date, to_: date):
    """
    Devuelve una agregación a nivel diario del parámetro especificado en el path. Serviría para representar el gráfico mensual por día.
    """
    if dao:
        result = await dao.get_day_aggregated(clientId, from_, to_, field)
        return result
    else:
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get('/range-aggregated')
async def get_range_aggregated(clientId: str, from_: date, to_: date):
    """
    Agregación total para el rango dado de todos los parámetros. Serviría para dar un status general de un rango temporal (por ejemplo el mes en curso)
    """
    if dao:
        result = await dao.get_range_aggregated(clientId, from_, to_)
        return result
    else:
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@app.get('/timestamp')
async def get_timestamp_data(clientId: str, timestamp: datetime.datetime, field: Optional[allowedFields] = None):
    """
    Agregación total para el rango dado de todos los parámetros. Serviría para dar un status general de un rango temporal (por ejemplo el mes en curso)
    """
    if dao:
        result = await dao.get_timestamp_data(clientId, timestamp, field)
        return result
    else:
        raise HTTPException(status_code=500, detail="Error interno del servidor")