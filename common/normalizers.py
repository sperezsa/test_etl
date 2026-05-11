import unicodedata

def clean_text(text: str) -> str:
    if not text: return ""
    # Normalizar a minúsculas y quitar espacios
    text = str(text).strip().lower()
    # Quitar acentos (NFKD descompone caracteres)
    text = "".join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c))
    # Quitar caracteres no ASCII (emojis y otros)
    return text.encode('ascii', 'ignore').decode('ascii')