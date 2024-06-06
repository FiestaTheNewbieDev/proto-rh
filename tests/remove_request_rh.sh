#!/bin/bash

read -p 'Your JWT: ' jwt
read -p 'Request ID: ' request_id

data='{
    "id": "'"$request_id"'"
}'

curl -X POST -H "Authorization: Bearer $jwt" -H "Content-Type: application/json" -d "$data" http://localhost:4242/rh/msg/remove

echo -e "\n"