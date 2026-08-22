from datetime import date, datetime

from sqlalchemy import inspect as sa_inspect


def model_to_dict(obj) -> dict:
    """Serialize a SQLAlchemy model instance to a JSON-safe dict."""
    result = {}
    for attr in sa_inspect(obj).mapper.column_attrs:
        value = getattr(obj, attr.key)
        if isinstance(value, datetime | date):
            value = value.isoformat()
        result[attr.key] = value
    return result
