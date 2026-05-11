from pydantic import BaseModel, EmailStr, field_validator, Field
from datetime import date 
from decimal import Decimal, InvalidOperation
from typing import Optional
from common.validators import validate_dni_logic, parse_generic_date
from common.normalizers import clean_text

ALLOWED_FORMATS = ['%Y-%m-%d', '%Y/%m/%d', '%y/%m/%d']
PAISES_OK = ['esp', 'ita', 'fra'] # Ya normalizados a minúsculas

# Aunque el origen tengan un tipo de dato x, el modelo de Pydantic debe representar el dato ya procesado.
class ClienteSchema(BaseModel):
    id: int
    nombre: str
    email: EmailStr
    saldo: Decimal
    nivel_riesgo: Optional[str] = "Bajo"
    documento: str
    pais: str
    comentarios: Optional[str] = ""
    fecha_alta: str #date

    @field_validator('nombre', 'pais', 'comentarios', 'documento', 'nivel_riesgo', mode='before')
    @classmethod
    def apply_normalization(cls, v):
        return clean_text(v)

    @field_validator('saldo')
    @classmethod
    def check_numeric_purity(cls, v):
        # Si viene de la BD como float o int, lo pasamos a string para la validación .isdigit
        str_v = str(v).replace('.', '').replace('-', '').strip()
    
        if not str_v.isdigit():
            raise ValueError(f"El valor '{v}' no es un número puro")
    
        return float(v)
    
    @field_validator('documento')
    @classmethod
    def check_dni(cls, v):
        return validate_dni_logic(v)

    @field_validator('fecha_alta')
    @classmethod
    def check_date(cls, v):
        return parse_generic_date(v, ALLOWED_FORMATS)

    @field_validator('pais')
    @classmethod
    def check_country_integrity(cls, v):
        if v not in PAISES_OK:
            raise ValueError(f"País '{v}' no permitido")
        return v