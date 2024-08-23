Inkitt Downloader
---

# THIS PROGRAM IS NOT COMPLETE
## IT IS VERY BUGGY RIGHT NOW
### Don't report any bugs yet, I know there are a lot

## Set Up

1. Clone the repository: `git clone https://github.com/AaronBenDaniel/InkittDownloader && cd InkittDownloader`
2. Build the image: `docker build . -t 'inkitt_downloader'`
3. Run the Container: `docker run -d -p 5043:80 inkitt_downloader`

### You MUST input login credentials, Inkitt requires them

This program is based on [TheOnlyWayUp's](https://github.com/TheOnlyWayUp) [Wattpad Downloader](https://github.com/TheOnlyWayUp/WattpadDownloader).
By based I mean it's just a copy but I made it download from Inkitt instead of Wattpad

*As you may be able to tell, the frontend has not been reskinned yet*