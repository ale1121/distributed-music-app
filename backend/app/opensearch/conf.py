import os
from pathlib import Path

OPENSEARCH_URL = os.getenv("OPENSEARCH_URL", "http://opensearch:9200")
INDEX_NAME = "catalog"
INDEX_DEFINITION_FILE = Path(__file__).with_name('catalog_index.json')

FUZZINESS = 2
MIN_MATCH = 75

OPENSEARCH_DOC_TYPES = ['artist', 'album', 'song']
