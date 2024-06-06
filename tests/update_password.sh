#!/bin/bash

read -p 'Email: ' email
read -s -p 'Password: ' password
printf '\n'
read -s -p 'New password: ' new_password
printf '\n'
read -s -p 'Repeat new password: ' repeat_new_password
printf '\n'

data='{
  "email": "'"$email"'",
  "password": "'"$password"'",
  "new_password": "'"$new_password"'",
  "repeat_new_password": "'"$repeat_new_password"'"
}'

curl -X POST -H "Content-Type: application/json" -d "$data" http://localhost:4242/user/password

echo -e "\n"