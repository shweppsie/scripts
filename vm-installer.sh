#!/bin/sh

NAME=hermes
MEMORY=128

virt-install \
--name=$NAME \
--ram=$MEMORY \
--location=http://ftp.nz.debian.org/debian/dists/stable/main/installer-amd64/ \
--os-type=linux \
--os-variant=debiansqueeze \
--disk=/img/$NAME.img,device=disk,bus=virtio,size=8,sparse=true,format=raw \
--network=bridge=lan,model=virtio \
--extra-args=console=ttyS0,115200

