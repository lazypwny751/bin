#!/usr/bin/env bash

while getopts ":s:i:v:t:h" opt; do
    case $opt in
        h) echo "$(basename "$0") [-s [SOURCE]] [-i [IMG_DESTINATION]] [-v [VID_DESTINATION]] [-t [TAGS]]"
           exit 0
           ;;
        s) SOURCE="$OPTARG"
           ;;
        i) IMG_DESTINATION="$OPTARG"
           ;;
        v) VID_DESTINATION="$OPTARG"
           ;;
        t) TAGS="$OPTARG"
           ;;
        \?) echo "INVALID OPTION -$OPTARG" >&2
            ;;
    esac
done

[ -z "$SOURCE" ] && SOURCE="$HOME/Dropbox/Camera Uploads"
[ -z "$IMG_DESTINATION" ] && IMG_DESTINATION="$HOME/Dropbox/Pictures"
[ -z "$VID_DESTINATION" ] && VID_DESTINATION="$HOME/Dropbox/Videos"
[ -z "$TAGS" ] && TAGS=(
        "createdate"
        "datetimeoriginal"
        "filemodifydate"
        "modifydate"
    )

FILE_FMT="%Y%m%d.%H%M%S%%c.%%le"
IMG_DIR_FMT="$IMG_DESTINATION/%Y/%m"
VID_DIR_FMT="$VID_DESTINATION/%Y/%m"
IMG_FILE_EXT=(
    '-ext arw'
    '-ext bmp'
    '-ext cr2'
    '-ext dng'
    '-ext gif'
    '-ext heic'
    '-ext heif'
    '-ext jpeg'
    '-ext jpg'
    '-ext k25'
    '-ext orf'
    '-ext nrw'
    '-ext png'
    '-ext psd'
    '-ext raw'
    '-ext svg'
    '-ext tif'
    '-ext tiff'
    '-ext webp'
)
VID_FILE_EXT=(
    '-ext avi'
    '-ext flv'
    '-ext m4v'
    '-ext mkv'
    '-ext mov'
    '-ext mp4'
    '-ext mpeg'
    '-ext mpg'
    '-ext mpv'
    '-ext ogg'
    '-ext ogv'
    '-ext vob'
    '-ext webm'
    '-ext wmv'
)

for tag in "${TAGS[@]}"; do
    exiftool "-filename<$tag"  -dateFormat "$FILE_FMT"    -recurse -ext "*" "$SOURCE" -q
    exiftool "-directory<$tag" -dateFormat "$IMG_DIR_FMT" -recurse ${IMG_FILE_EXT[*]} "$SOURCE" -q
    exiftool "-directory<$tag" -dateFormat "$VID_DIR_FMT" -recurse ${VID_FILE_EXT[*]} "$SOURCE" -q
done
