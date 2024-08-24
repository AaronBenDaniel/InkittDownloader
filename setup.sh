#!/bin/bash

echo "You might need to run me as root depending on how Docker is configured"
git checkout main
git pull
docker build . -t inkitt_downloader
docker run -d -p 5043:80 --restart=unless-stopped inkitt_downloader