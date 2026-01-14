import os

OPENSEARCH_URL = os.getenv("OPENSEARCH_URL", "http://opensearch:9200")
INDEX_NAME = "catalog"

FUZZINESS = 3
MIN_MATCH = 75

OPENSEARCH_DOC_TYPES = ['artist', 'album', 'song']
