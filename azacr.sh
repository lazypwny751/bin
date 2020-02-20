#!/usr/bin/env bash
# infinite loop to get simple yes or no user input
ask() {
    local question="$1"

    while :; do
	# -e for readline bindings
	# -r to not mangle backslashes
	# -n 1 for execution without return
	read -rep "$question " ans
	case $ans in
	    [Yy][Ee][Ss]|[Yy])
		return 0
		;;
	    [Nn][Oo]|[Nn])
		return 1
		;;
	    [Qq][Uu][Ii][Tt]|[Qq])
		exit 0
		;;
	    *)
		echo "$ans is invalid. Enter (y)es, (n)o or (q)uit."
		;;
	esac
    done
}

get_old_manifests() {
    local registry="$1" repository="$2" older_than="$3"

    echo "Getting manifests from $registry/$repository older than $older_than..."
    IFS=$'\n'
    OLD_MANIFESTS=($(az acr repository show-manifests \
			--name "$registry" \
			--repository "$repository" \
			--orderby time_asc \
			--output tsv \
			--query "[?timestamp < '$older_than'].[digest, timestamp]"))
    unset IFS
}

show_old_manifests() {
    local registry="$1" repository="$2" older_than="$3"

    echo "Found ${#OLD_MANIFESTS[@]} older than $older_than in $registry/$repository."
    if ask "Would you like to view them?"; then
	for manifest in "${OLD_MANIFESTS[@]}"; do
	    echo "$manifest"
	done
    fi
}

delete_old_manifests() {
    local registry="$1" image="$2" older_than="$3"

    if ask "Would you like to delete all manifests older than $older_than in $registry/$image?"; then
	for manifest in "${OLD_MANIFESTS[@]}"; do
	    manifest="$(echo $manifest | awk '{print $1}')"
	    az acr repository delete \
	       --name "$registry" \
	       --image "$image@$manifest" \
	       --yes
	done
    fi
}

get_old_manifests "$@"
show_old_manifests "$@"
delete_old_manifests "$@"
