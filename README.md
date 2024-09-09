Inkitt Downloader
---

# Broken right now because Inkitt cracked down on scraping

# Not all stories download properly...
###  for some reason
If anyone can figure out why that'd be helpful

---

![](/pics/screenshot.webp)

This is a docker container that hosts a webserver on `http://{ip}:5043`. Input an Inkitt story URL or story ID, input your Inkitt login credentials, and click "Download". After waiting for the program to download and compile the book (it can take a minute or so) the user will be prompted to download a .epub file of the book.

### This is a piece of server software that hosts a webpage accessible to all devices that can access port `5043` of the host machine.

## Set Up

This program requires Docker: https://docs.docker.com/engine/install/

1. Clone the repository: `git clone https://github.com/AaronBenDaniel/InkittDownloader`
2. CD into the repo: `cd InkittDownloader`
3. Run `setup.sh`: `./setup.sh`

### You MUST input login credentials, Inkitt requires them

This program is based on [TheOnlyWayUp's](https://github.com/TheOnlyWayUp) [Wattpad Downloader](https://github.com/TheOnlyWayUp/WattpadDownloader).
By based I mean it's just a copy but I made it download from Inkitt instead of Wattpad
