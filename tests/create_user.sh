#!/bin/bash

read -p 'Email: ' email
read -s -p 'Password: ' password
printf '\n'
read -p 'Firstname: ' firstname
read -p 'Lastname: ' lastname
read -p 'Birthday date: ' birthday_date
read -p 'Adress: ' adress
read -p 'Postal code: ' postal_code

data='{
  "email": "'"$email"'",
  "password": "'"$password"'",
  "firstname": "'"$firstname"'",
  "lastname": "'"$lastname"'",
  "birthday_date": "'"$birthday_date"'",
  "adress": "'"$adress"'",
  "postal_code": "'"$postal_code"'"
}'

curl -X POST -H "Content-Type: application/json" -d "$data" http://localhost:4242/user/create

echo -e "\n"