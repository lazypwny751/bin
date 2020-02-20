#!/usr/bin/env bash

ask() {
    local question="$1"

    while :; do
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

###############################################################################
#                                OLD MANIFESTS                                #
###############################################################################
get_old_manifests() {
    local registry="$1" repository="$2" older_than="$3"

    echo "Getting manifests from $registry/$repository last updated before $older_than..."
    IFS=$'\n'
    OLD_MANIFESTS=($(az acr repository show-manifests \
			--name "$registry" \
			--repository "$repository" \
			--orderby time_asc \
			--output tsv \
			--detail \
			--query "[?lastUpdateTime < '$older_than'].[digest, tags, createdTime, lastUpdateTime]"))
    unset IFS

    if [[ "${#OLD_MANIFESTS[@]}" -lt 1 ]]; then
	echo "No manifests last updated before $older_than in $registry/$repository."
	exit 0
    fi
}

show_old_manifests() {
    local registry="$1" repository="$2" older_than="$3"

    echo "Found ${#OLD_MANIFESTS[@]} older than $older_than in $registry/$repository."
    if ask "Would you like to view them?"; then
	for manifest in "${OLD_MANIFESTS[@]}"; do
	    echo "$manifest"
	done | "$PAGER"
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

###############################################################################
#                          UNTAGGED (ORPHANED) IMAGES                         #
###############################################################################
get_untagged_images() {
    local registry="$1" repository="$2"

    echo "Getting untagged (orphaned) images from $registry/$repository..."
    IFS=$'\n'
    UNTAGGED_IMAGES=($(az acr repository show-manifests \
			  --name "$registry" \
			  --repository "$repository" \
			  --orderby time_asc \
			  --output tsv \
			  --detail \
			  --query "[?tags[0]==null].[digest, tags, createdTime, lastUpdateTime]"))
    unset IFS

    if [[ "${#UNTAGGED_IMAGES[@]}" -lt 1 ]]; then
	echo "No untagged (orphaned) manifests in $registry/$repository."
	exit 0
    fi
}

show_untagged_images() {
    local registry="$1" repository="$2"

    echo "Found ${#UNTAGGED_IMAGES[@]} untagged (orphaned) images in $registry/$repository."
    if ask "Would you like to view them?"; then
	for image in "${UNTAGGED_IMAGES[@]}"; do
	    echo "$image"
	done | "$PAGER"
    fi
}

delete_untagged_images() {
    local registry="$1" image="$2"

    if ask "Would you like to delete all untagged (orphaned) images in $registry/$image?"; then
	for manifest in "${UNTAGGED_IMAGES[@]}"; do
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

get_untagged_images "$@"
show_untagged_images "$@"
delete_untagged_images "$@"
