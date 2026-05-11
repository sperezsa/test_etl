from datetime import datetime

def validate_dni_logic(dni: str) -> str:
    letras = "TRWAGMYFPDXBNJZSQVHLCKE"
    dni = dni.upper().replace(" ", "").replace("-", "")
    if len(dni) != 9:
        raise ValueError("Longitud de DNI incorrecta (deben ser 9 caracteres)")
    
    numero_str = dni[:8]
    if not numero_str.isdigit():
        raise ValueError("Los primeros 8 caracteres del DNI deben ser números")
    
    if letras[int(numero_str) % 23] != dni[8]:
        raise ValueError(f"DNI inválido: Letra de control incorrecta para {dni}")
    return dni

def parse_generic_date(date_str: str, formats: list) -> datetime:
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Formato de fecha inválido. Formatos aceptados: {formats}")