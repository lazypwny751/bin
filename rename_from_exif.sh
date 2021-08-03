#!/usr/bin/env bash

NC="$(tput sgr0)"
RED="$(tput setaf 1)"
YEL="$(tput setaf 3)"
MAG="$(tput setaf 5)"
CYN="$(tput setaf 6)"

usage() {
    echo "
$(basename "$0") [-s [SOURCE]] [-i [IMG_DESTINATION]] [-v [VID_DESTINATION]] [-t [TAGS]]
"
}

while getopts ":s:i:v:t:h" opt; do
    case $opt in
        h) usage
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
        \?) echo "${RED}INVALID OPTION -$OPTARG${NC}" >&2
            usage
            exit 1
            ;;
    esac
done

[ -z "$SOURCE" ] && SOURCE="$HOME/Dropbox/Camera Uploads"
[ -d "$SOURCE" ] || { echo "${RED}$SOURCE doesn't exist. Aborting!${NC}"; exit 1; }
[ -z "$IMG_DESTINATION" ] && IMG_DESTINATION="$HOME/Dropbox/Pictures"
[ -d "$IMG_DESTINATION" ] || {
    echo "${RED}$IMG_DESTINATION doesn't exist. Aborting!${NC}"; exit 1;
}
[ -z "$VID_DESTINATION" ] && VID_DESTINATION="$HOME/Dropbox/Videos"
[ -d "$VID_DESTINATION" ] || {
    echo "${RED}$VID_DESTINATION doesn't exist. Aborting!${NC}"; exit 1;
}
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
    'arw'
    'bmp'
    'cr2'
    'dng'
    'eps'
    'gif'
    'heic'
    'heif'
    'jpeg'
    'jpg'
    'k25'
    'orf'
    'nef'
    'nrw'
    'png'
    'psd'
    'raw'
    'sr2'
    'svg'
    'tif'
    'tiff'
    'webp'
)
for ext in "${IMG_FILE_EXT[@]}"; do
    IMG_FILE_EXT_OPTS+="-ext $ext "
done
for ext in "${IMG_FILE_EXT[@]}"; do
    if [ "$ext" == "${IMG_FILE_EXT[-1]}" ]; then
        IMG_FILE_FIND_REGEX+=".*\.$ext"
    else
        IMG_FILE_FIND_REGEX+=".*\.$ext\|"
    fi
done

VID_FILE_EXT=(
    'avi'
    'flv'
    'm4v'
    'mkv'
    'mov'
    'mp4'
    'mpeg'
    'mpg'
    'mpv'
    'ogg'
    'ogv'
    'vob'
    'webm'
    'wmv'
)
for ext in "${VID_FILE_EXT[@]}"; do
    VID_FILE_EXT_OPTS+="-ext $ext "
done
for ext in "${VID_FILE_EXT[@]}"; do
    if [ "$ext" == "${VID_FILE_EXT[-1]}" ]; then
        VID_FILE_FIND_REGEX+=".*\.$ext"
    else
        VID_FILE_FIND_REGEX+=".*\.$ext\|"
    fi
done

COMMON_OPTS="-recurse -extractEmbedded -ignoreMinorErrors"

for tag in "${TAGS[@]}"; do
    if [ -n "$( find "$SOURCE" -prune -empty 2>/dev/null )" ]; then
        echo "${CYN}$SOURCE is empty. Nothing to do.${NC}"
        break
    fi
    echo "${YEL}Renaming all files in $SOURCE to $FILE_FMT using $tag... ${NC}"
    exiftool "-filename<$tag" -dateFormat "$FILE_FMT" -ext "*" "$COMMON_OPTS" "$SOURCE"
    echo "${YEL}Moving all image files in $SOURCE to $IMG_DIR_FMT using $tag... ${NC}"
    exiftool "-directory<$tag" -dateFormat "$IMG_DIR_FMT" $IMG_FILE_EXT_OPTS $COMMON_OPTS "$SOURCE"
    echo "${YEL}Moving all video files in $SOURCE to $VID_DIR_FMT using $tag... ${NC}"
    exiftool "-directory<$tag" -dateFormat "$VID_DIR_FMT" $VID_FILE_EXT_OPTS $COMMON_OPTS "$SOURCE"
done

check_for_inappropriate_files() {
    local dir="$1" file_regex="$2"
    printf "${YEL}Checking $dir for image files... ${NC}"
    readarray -d '' found_files < <(find "$dir" -iregex "$file_regex" -print0)
    if [ "${#found_files[@]}" == 0 ]; then
        printf "${CYN}Nothing to see here :-)${NC}\n"
    else
        printf "${MAG}Found ${#found_files[@]}:${NC}\n"
        for f in "${found_files[@]}"; do
            echo "$f"
        done
    fi
}

check_for_inappropriate_files "$IMG_DESTINATION" "$VID_FILE_FIND_REGEX"
check_for_inappropriate_files "$VID_DESTINATION" "$IMG_FILE_FIND_REGEX"
