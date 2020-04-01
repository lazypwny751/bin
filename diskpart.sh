#!/usr/bin/env bash

[ "$(id -u)" -ne 0 ] && { echo "This script must be run as root."; exit 1; }
[ -n "$1" ] && disk="$1" || { echo "$(basename "$0") [DISK]"; exit 1; }

sgdisk --zap-all "$disk" && partprobe "$disk" &&
    parted --script "$disk" mklabel gpt mkpart primary ext4 0% 100% &&
    blockdev --getalignoff "$disk"
