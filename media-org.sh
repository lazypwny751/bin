#!/usr/bin/env bash
while getopts ":s:d:t:h" opt; do
    case $opt in
	h) echo "$(basename "$0") [-s [SOURCE]] [-d [DESTINATION]] [-t [TAG]]"
	   exit 0
	   ;;
	s) SRC="$OPTARG"
	   ;;
	d) DST="$OPTARG"
	   ;;
	t) TAG="$OPTARG"
	   ;;
	\?) echo "INVALID OPTION -$OPTARG" >&2
	    ;;
    esac
done

[ -z "$SRC" ] && SRC="$HOME/Dropbox/Camera Uploads"
[ -z "$DST" ] && DST="$HOME/Dropbox/Pictures"
[ -z "$TAG" ] && TAG="createdate"

FILE_FMT="%Y%m%d.%H%M%S%%c.%%le"
DIR_FMT="$DST/%Y/%m"

exiftool "-filename<$TAG" -dateFormat "$FILE_FMT" -recurse -extension "*" "$SRC"
exiftool "-directory<$TAG" -dateFormat "$DIR_FMT" -recurse -extension "*" "$SRC"
