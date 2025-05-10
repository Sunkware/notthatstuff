#!/bin/sh

# Requires yt-dlp, install/update with "$ pip install -U yt-dlp"

yt-dlp -f "bestaudio" $1
