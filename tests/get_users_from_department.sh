#!/bin/bash

read -p 'Your JWT: ' jwt
read -p 'Department ID: ' department_id

curl -X GET -H "Authorization: Bearer $jwt" http://localhost:4242/departements/$department_id/users

echo -e "\n"