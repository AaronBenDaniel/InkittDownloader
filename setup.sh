#!/bin/bash

if [ "$EUID" -ne 0 ]
    then echo -e "\033[1;31mYou might need to run me as root depending on how Docker is configured\033[0m"
fi
git checkout main
git pull
docker build . -t inkitt_downloader
docker run -d -p 5043:80 --restart=unless-stopped --name inkitt-downloader inkitt_downloader