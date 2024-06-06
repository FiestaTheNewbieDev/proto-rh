#!/bin/bash

read -p 'Your JWT: ' jwt
read -p 'Your ID: ' user_id
read -p 'The content of your request: ' content

data='{
    "user_id": "'"$user_id"'",
    "content": "'"$content"'"
}'

curl -X POST -H "Authorization: Bearer $jwt" -H "Content-Type: application/json" -d "$data" http://localhost:4242/rh/msg/add

echo -e "\n"