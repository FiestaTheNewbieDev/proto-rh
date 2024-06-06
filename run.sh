#!/bin/bash

sudo service postgresql start

uvicorn src.main:app --port 4242 --reload