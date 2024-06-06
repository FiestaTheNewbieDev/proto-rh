#!/bin/bash

read -p 'Your JWT: ' jwt

curl -X GET -H "Authorization: Bearer $jwt" http://localhost:4242/rh/msg/

echo -e "\n"