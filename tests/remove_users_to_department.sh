#!/bin/bash

read -p 'Your JWT: ' jwt
read -p 'Department ID: ' department_id

user_ids='['
while true; do
    read -p 'User ID (Enter q to close list): ' user_id
    if [ "$user_id" == "q" ]; then
        break
    else
        user_ids="$user_ids $user_id,"
    fi
done
user_ids="${user_ids%,}"
user_ids="$user_ids]"

data='{
    "user_ids": '$user_ids'
}'

echo $data

curl -X POST -H "Authorization: Bearer $jwt" -H "Content-Type: application/json" -d "$data" http://localhost:4242/departements/$department_id/users/remove

echo -e "\n"