#!/bin/sh
if [ $# -eq 0 ]; then
    echo "Please pass the name server IP as parameter"
    return
fi

# Persists the DNS server IP addresses in the management node
# Takes dns server IPs as parameters

sudo mv /etc/apt/sources.list.dBKP/ /etc/apt/sources.list.d
sudo mv /etc/apt/sources.listBKP /etc/apt/sources.list
echo "enabled software installation"
sudo apt update
sudo apt-get install resolvconf -y
echo "installed resolvconf"
sudo systemctl enable --now resolvconf.service
echo "nameservers ${1} ${2}"
sudo echo "nameserver ${1}"  >> /etc/resolvconf/resolv.conf.d/head
sudo echo "nameserver ${2}"  >> /etc/resolvconf/resolv.conf.d/head
reboot