#!/bin/bash

read -p 'Your JWT: ' jwt
read -p 'User ID: ' user_id

curl -X GET -H "Authorization: Bearer $jwt" http://localhost:4242/user/$user_id

echo -e "\n"