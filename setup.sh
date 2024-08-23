#!/bin/bash

git pull
git checkout main
git pull
sudo docker build . -t inkitt_downloader
sudo docker compose up -d

