# Tests

This directory contains a Postman/Newman test suite (48 requests, 51 assertions), covering authentication, access control, CRUD operations, search indexing and streaming functionality

## Contents

* [`collection.json`](collection.json) - tests collection
* [`env.json`](env.json) - local environment variables used by the collection
* [`sample-data/`](sample-data) - sample files used for upload tests
* [`test-results`](test-results) - example Newman output

## What is covered

The test collection validates end-to-end behaviors, including:
* Authentication and token retrieval through Keycloak
* Role-based access control for user, artist and admin routes
* Album ownership checks
* Consistency rules for artist requests
* Album and song input and upload validation
* Public/private catalog visibility
* OpenSearch search results
* Signed streaming URL validation
* HTTP range requests for audio streaming
* Load distribution across streaming replicas
* Deletion consistency across database, search index and streaming service
* Grafana availability

## Running the tests

From this directory:

```bash
newman run collection.json -e env.json --delay-request 300
```

A small request delay is used so OpenSearch indexing and deletion operations have time to become visible

[Example test run output](test-results)
