#!/bin/bash

read -p 'Email: ' email
read -s -p 'Password: ' password
printf '\n'

data='{
  "email": "'"$email"'",
  "password": "'"$password"'"
}'

curl -X POST -H "Content-Type: application/json" -d "$data" http://localhost:4242/connect

echo -e "\n"