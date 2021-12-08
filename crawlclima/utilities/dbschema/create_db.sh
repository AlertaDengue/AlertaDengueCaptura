#!/bin/bash

echo -e "\n >>>  Create database and import schemas <<< \n"

echo $(pwd)

createdb -h localhost -U postgres dengue

psql -h localhost dengue < crawlclima/utilities/dbschema/roles-infodengue_roles.sql

gunzip -c crawlclima/utilities/dbschema/schemas_dengue_2021_10_04.sql.gz | psql -h localhost -U postgres dengue
