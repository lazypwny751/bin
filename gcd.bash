#!/usr/bin/env bash

gcd() {
    local -a abspaths
    local relpath="$1"

    readarray -d '' abspaths < <(find "$HOME/src" \
				      -maxdepth 10 \
				      -type d \
				      -name ".git" \
				      -print0 | \
				     sed 's/\/\.git//g')

    for path in "${abspaths[@]}"; do
	if [[ "$path" =~ .*"$relpath"$ ]]; then
	    # echo "$p"
	    # export PWD="$p"
	    cd "$path" || exit 1
	    echo "$PWD"
	fi
    done
}

gcd "$1"
# readarray -d ' ' RELPATHS < <(find "$HOME/src" \
    #				   -maxdepth 10 \
    #				   -type d \
    #				   -name ".git" \
    #				   -printf "%P " | \
    #				  sed 's/\/\.git//g')

# echo "${ABSPATHS[@]}"
# echo "${RELPATHS[@]}"

# echo "$1"
