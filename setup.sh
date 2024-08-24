#!/bin/bash

echo -e "\033[1;31mYou might need to run me as root depending on how Docker is configured\033[0m"
git checkout main
git pull
docker build . -t inkitt_downloader
docker run -d -p 5043:80 --restart=unless-stopped inkitt_downloader