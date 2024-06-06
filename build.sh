#!/bin/bash

# Vérification des paramètres
developer_mode=0
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --dev)
            developer_mode=1
            ;;
        *)
            echo -e '\e[31mUnknown option\e[0m'
            exit 1
            ;;
    esac
    shift
done

# Installation des packages linux destinés au développeur
if [ "$developer_mode" -eq 1 ]; then
    echo -e '\e[34mInstallation des packages linux destinés au développeur\e[0m'
    sudo apt-get install pycodestyle pylint
fi

# Installation des packages linux
echo -e '\e[34mInstallation des packages linux\e[0m'
sudo apt-get install curl python3 python3-pip uvicorn postgresql postgresql-client

# Installation des packages python
echo -e '\e[34mInstallation des packages python\e[0m'
pip3 install --break-system-packages -r requirements.txt