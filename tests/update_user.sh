#!/bin/bash

read -p 'Your JWT: ' jwt
read -p 'ID: ' id
read -p 'Email: ' email
read -p 'Firstname: ' firstname
read -p 'Lastname: ' lastname
read -p 'Birthday date: ' birthday_date
read -p 'Adress: ' adress
read -p 'Postal code: ' postal_code
read -p 'Role: ' role

data='{'

if [ -n "$id" ]; then
  data="$data \"id\": \"$id\","
fi

if [ -n "$email" ]; then
  data="$data \"email\": \"$email\","
fi

if [ -n "$firstname" ]; then
  data="$data \"firstname\": \"$firstname\","
fi

if [ -n "$lastname" ]; then
  data="$data \"lastname\": \"$lastname\","
fi

if [ -n "$birthday_date" ]; then
  data="$data \"birthday_date\": \"$birthday_date\","
fi

if [ -n "$adress" ]; then
  data="$data \"adress\": \"$adress\","
fi

if [ -n "$postal_code" ]; then
  data="$data \"postal_code\": \"$postal_code\","
fi

if [ -n "$role" ]; then
  data="$data \"role\": \"$role\","
fi

data=${data%,}

data="$data }"

curl -X POST -H "Authorization: Bearer $jwt" -H "Content-Type: application/json" -d "$data" http://localhost:4242/user/update

echo -e "\n"