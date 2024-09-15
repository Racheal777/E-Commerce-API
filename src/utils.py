from flask import jsonify
from typing import Union, Dict, List, Any
from sqlalchemy.ext.declarative import DeclarativeMeta

def sqlalchemy_obj_to_dict(obj):

    if isinstance(obj.__class__, DeclarativeMeta):
        return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
    return obj


def create_response(
    data: Union[Dict, List, Any] = None,
    message: str = "",
    status: int = 200,
    error: Union[str, List[str], Dict[str, Any]] = None
) -> tuple:

    response = {
        "status": status,
        "message": message
    }

    if data is not None:
        if isinstance(data, list):
            response["data"] = [sqlalchemy_obj_to_dict(item) for item in data]
        else:
            response["data"] = sqlalchemy_obj_to_dict(data)

    if error is not None:
        response["error"] = error

    return jsonify(response), status

