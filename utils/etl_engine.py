import pandas as pd
from pydantic import ValidationError

class ETLEngine:
    @staticmethod
    def process(data_list: list, schema_class):
        valid_records = []
        error_logs = []
        seen_ids = set()

        for raw_item in data_list:
            try:
                # 1. Check de duplicados (Integridad)
                record_id = raw_item.get('id')
                if record_id in seen_ids:
                    raise ValueError(f"ID Duplicado: {record_id}")
                
                # 2. Validación y Transformación con Pydantic
                validated_model = schema_class(**raw_item)
                
                valid_records.append(validated_model.model_dump())
                seen_ids.add(record_id)

            except ValidationError as e:
                # .json() devuelve un string detallado con cada campo fallido
                raw_item['error_reason'] = e.json()
                error_logs.append(raw_item)
            except ValueError as e:
                raw_item['error_reason'] = str(e)
                error_logs.append(raw_item)


        return pd.DataFrame(valid_records), pd.DataFrame(error_logs)