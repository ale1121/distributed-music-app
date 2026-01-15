from .conf import MIN_MATCH, FUZZINESS


def get_query(query, limit):
    return {
        "size": limit,
        "query": query,
        "sort": ["_score"]
    }

def match_name(name):
    return {
        "match": {
            "name": {
                "query": name,
                "minimum_should_match": f"{MIN_MATCH}%",
                "fuzziness": FUZZINESS
            }
        }
    }

def multi_match_name(name):
    return {
        "multi_match": {
            "query": name,
            "type": "bool_prefix",
            "fields": ["name", "name._2gram", "name._3gram"]
        }
    }

def name_type_query(name_query, type):
    return {
        "bool": {
            "must": [
                name_query,
                {"term": {"type": type}}
            ]
        }
    }
