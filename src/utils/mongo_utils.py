from bson import ObjectId


def filter_by_id(id: str) -> dict:
    return {'_id': ObjectId(id)}


def filter_by_name(name: str) -> dict:
    return {'name': name}
