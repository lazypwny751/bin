#!/usr/bin/env bash
[ -n "$1" ] && SRC="$1" || SRC="$HOME/Dropbox/Camera Uploads"
[ -n "$2" ] && DST="$2" || DST="$HOME/Dropbox/Pictures"

FILE_FMT="%Y%m%d.%H%M%S%%c.%%le"
DIR_FMT="$DST/%Y/%m"

# exiftool -quiet '-filename<contentcreatedate' -dateFormat "$FILE_FMT" -recurse -extension "*" "$SRC"
# exiftool -quiet '-directory<contentcreatedate' -dateFormat "$DIR_FMT" -recurse -extension "*" "$SRC"
exiftool -quiet '-filename<createdate' -dateFormat "$FILE_FMT" -recurse -extension "*" "$SRC"
exiftool -quiet '-directory<createdate' -dateFormat "$DIR_FMT" -recurse -extension "*" "$SRC"
# exiftool -quiet '-filename<datetimeoriginal' -dateFormat "$FILE_FMT" -recurse -extension "*" "$SRC"
# exiftool -quiet '-directory<datetimeoriginal' -dateFormat "$DIR_FMT" -recurse -extension "*" "$SRC"
# exiftool -quiet '-filename<filemodifydate' -dateFormat "$FILE_FMT" -recurse -extension "*" "$SRC"
# exiftool -quiet '-directory<filemodifydate' -dateFormat "$DIR_FMT" -recurse -extension "*" "$SRC"
