from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from decimal import Decimal 
from datetime import date 

class TransaccionSchema(BaseModel):
    id: int
    cliente_id: int 
    monto: Decimal
    tipo: str
    fecha: date


    # Validamos que cliente_id sea informado y sea un entero positivo
    cliente_id: int = Field(..., description="ID del cliente asociado a la transacción")
    
    # Validamos monto como número real (float) y mayor que cero
    # monto: float = Field(..., gt=0, description="Monto de la transacción, debe ser mayor a 0")
    
    # Validamos tipo de transacción (ej. 'ingreso', 'egreso')
    tipo: str = Field(..., min_length=1, description="Tipo de transacción (no puede estar vacío)")
    
    # La fecha se valida automáticamente como objeto datetime
    fecha: datetime = Field(default_factory=datetime.now, description="Fecha y hora de la transacción")

    @field_validator('tipo')
    @classmethod
    def validar_tipo_limpio(cls, v: str) -> str:
        # Eliminamos espacios en blanco y verificamos que quede contenido
        if not v.strip():
            raise ValueError('El tipo de transacción no puede consistir solo en espacios')
        return v.strip()

