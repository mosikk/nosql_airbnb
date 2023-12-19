from bson import ObjectId


def filter_by_id(id: str) -> dict:
    return {'_id': ObjectId(id)}
