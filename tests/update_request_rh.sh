#!/bin/bash

read -p 'Your JWT: ' jwt
read -p 'Request ID: ' request_id
read -p 'The new content of the request: ' content

data='{
    "id": "'"$request_id"'",
    "content": "'"$content"'"
}'

curl -X POST -H "Authorization: Bearer $jwt" -H "Content-Type: application/json" -d "$data" http://localhost:4242/rh/msg/update

echo -e "\n"