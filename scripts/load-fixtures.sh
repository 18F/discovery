#!/usr/bin/env bash
# Load data for the GSA PSHC discovery application, per the README instructions.

# Load vendor related fixtures

./manage.py loaddata vendors/fixtures/naics.json
./manage.py loaddata vendors/fixtures/setasides.json
./manage.py loaddata vendors/fixtures/pools.json # reqs: naics
./manage.py loaddata vendors/fixtures/vendors.json # reqs: setasides
./manage.py loaddata vendors/fixtures/poolpiids.json # reqs: pool, vendor
./manage.py loaddata vendors/fixtures/samloads.json

# Load contract related fixtures

./manage.py loaddata contract/fixtures/contracts.json #reqs: naics, vendor, piid
./manage.py loaddata contract/fixtures/fpdsloads.json #reqs: vendor
