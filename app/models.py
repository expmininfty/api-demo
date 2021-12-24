from enum import Enum
from pydantic import BaseModel

class allowedFields(str, Enum):
    power = "power"
    maximeter = "maximeter"
    reactivePower = "reactivePower"
    powerFactor = "powerFactor"
    energy = "energy"
    reactiveEnergy = "reactiveEnergy"
    intensity = "intensity"
    voltage = "voltage"
