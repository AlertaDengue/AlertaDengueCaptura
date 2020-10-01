#!/usr/bin/env bash


# CLIENT_SECRET = '*'
sed -i -e "s|^CLIENT_SECRET=.*$|CLIENT_SECRET=$CLIENT_SECRET|g" docker/satellite/.env
# CLIENT_ID='*'
sed -i -e "s|^CLIENT_ID=.*$|CLIENT_ID=$CLIENT_ID|g" docker/satellite/.env
# PROJECT_ID='*'
sed -i -e "s|^PROJECT_ID=.*$|PROJECT_ID=$PROJECT_ID|g" docker/satellite/.env
# REFRESH_TOKEN='*'
sed -i -e "s|^REFRESH_TOKEN=.*$|REFRESH_TOKEN=$REFRESH_TOKEN|g" docker/satellite/.env
# ACCESS_TOKEN
sed -i -e "s|^ACCESS_TOKEN=.*$|ACCESS_TOKEN=$ACCESS_TOKEN|g" docker/satellite/.env

echo "Environment variables were exported!"
