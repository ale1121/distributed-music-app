from pathlib import Path
import requests
import json
from .conf import OPENSEARCH_URL, INDEX_NAME


def check_index_exists():
    """ Check if index already exists """
    r = requests.head(f"{OPENSEARCH_URL}/{INDEX_NAME}")
    if r.status_code == 200:
        return True
    if r.status_code == 404:
        return False
    raise RuntimeError(f"Unexpected response from OpenSearch: {r.status_code} {r.text}")
    

def create_index():
    """ Create catalog index """

    # load index definition
    index_file = Path(__file__).with_name('catalog_index.json')
    with index_file.open('r') as f:
        index_def = json.load(f)

    # create index
    r = requests.put(f"{OPENSEARCH_URL}/{INDEX_NAME}", json=index_def)
    if r.status_code != 200:
        raise RuntimeError(f"Error creating index: {r.status_code} {r.text}")
