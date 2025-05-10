#!/bin/sh

# Requires yt-dlp, install/update with "$ pip install -U yt-dlp"

# Assumes that urls.txt contains
#
# url1
# url2
# ...
# urlN
#
# where each url is e.g. https://www.youtube.com/watch?v=0123456789A
# Last line must end with newline too, otherwise "while read url" skips it.

if [ "$(uname)" == "Darwin" ]; then
	GEPLSU_DATE_ALIAS=gdate
	GEPLSU_SED_ALIAS=gsed
else
	GEPLSU_DATE_ALIAS=date
	GEPLSU_SED_ALIAS=sed
fi

GEPLSU_DOWNLOADER_ALIAS=yt-dlp
GEPLSU_FORMAT=ttml
GEPLSU_LANG=ru-orig
GEPLSU_LIST="urls.txt"
GEPLSU_TEMPLATE=sub

while read url; do
	echo "Downloading from $url ..."
	TIMESTAMP="$($GEPLSU_DOWNLOADER_ALIAS --no-download --write-auto-subs --sub-langs $GEPLSU_LANG --sub-format $GEPLSU_FORMAT -o $GEPLSU_TEMPLATE --print timestamp --no-simulate $url)"
	FILENAME="$($GEPLSU_DATE_ALIAS -d @$TIMESTAMP +D_%Y_%m_%d_T_%H_%M_%S).txt"
	echo "Renaming to $FILENAME ..."
	mv $GEPLSU_TEMPLATE.$GEPLSU_LANG.$GEPLSU_FORMAT $FILENAME
	echo "Cleaning..."
	$GEPLSU_SED_ALIAS -i -r -z -e 's/<[^>]*>//g' -e 's/\n[\n]+//g' -e 's/\n/ /g' -e 's/\[[^]]*\]//g' -e 's/[ ]+/ /g' -e 's/&quot;/"/g' $FILENAME
	echo "Done"
	echo ""
done < "$GEPLSU_LIST"
