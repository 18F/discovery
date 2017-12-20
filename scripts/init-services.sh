#!/usr/bin/env bash

cf create-service aws-rds shared-psql discovery-db
cf create-service redis32 standard discovery-redis