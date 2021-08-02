#!/usr/bin/env bash

NC="$(tput sgr0)"
GRN="$(tput setaf 2)"
YEL="$(tput setaf 3)"
CYN="$(tput setaf 6)"

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
COMMON_OPTIONS=(
    -recurse
    -extractEmbedded
    -ignoreMinorErrors
)

for tag in "${TAGS[@]}"; do
    if [ -n "$( find "$SOURCE" -prune -empty 2>/dev/null )" ]; then
        echo "${CYN}$SOURCE is empty. Nothing to do.${NC}"
        break
    fi
    echo "${YEL}Renaming all files in $SOURCE to $FILE_FMT using $tag... ${NC}"
    exiftool "-filename<$tag" -dateFormat "$FILE_FMT" -ext "*" ${COMMON_OPTIONS[*]} "$SOURCE"
    echo "${YEL}Moving all image files in $SOURCE to $IMG_DIR_FMT using $tag... ${NC}"
    exiftool "-directory<$tag" -dateFormat "$IMG_DIR_FMT" ${IMG_FILE_EXT[*]} ${COMMON_OPTIONS[*]} "$SOURCE"
    echo "${YEL}Moving all video files in $SOURCE to $VID_DIR_FMT using $tag... ${NC}"
    exiftool "-directory<$tag" -dateFormat "$VID_DIR_FMT" ${VID_FILE_EXT[*]} ${COMMON_OPTIONS[*]} "$SOURCE"
done

echo "${YEL}Checking $IMG_DESTINATION for video files...${NC}"
find "$IMG_DESTINATION" -regex '.*\.mp4\|.*\.mov\|.*\.webm\|.*\.m4v\|.*\.mkv'
echo "${YEL}Checking $VID_DESTINATION for image files...${NC}"
find "$VID_DESTINATION" -regex '.*\.jpeg\|.*\.jpg\|.*\.png\|.*\.webp\|.*\.gif'
