#!/bin/sh

if [ $# -ne 3 ]; then
	echo "Usage: $0 NAME MEMORY SIZE"
fi

NAME=$1
MEMORY=$2 #size in MB
SIZE=$3 #size in GB

virt-install \
--name=${NAME} \
--ram=${MEMORY} \
--location=http://ftp.nz.debian.org/debian/dists/stable/main/installer-amd64/ \
--os-type=linux \
--os-variant=debiansqueeze \
--disk=/img/${NAME}.img,device=disk,bus=virtio,size=${SIZE},sparse=true,format=raw \
--network=bridge=lan,model=virtio \
--extra-args=console=ttyS0,115200

