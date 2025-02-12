#!/bin/bash

ARCH=$(uname -m)

if [ "$ARCH" == "x86_64" ]; then
    echo "64-bit architecture detected."
  	sudo cp libsnap7/x86_64-linux/libsnap7.so /usr/lib/
	echo "libsnap7.so copied to /ust/lib/libsnap7.so"

elif [ "$ARCH" == "i386" ] || [ "$ARCH" == "i686" ]; then
    echo "32-bit architecture detected."
	sudo cp ./libsnap7/i386-linux/libsnap.so /usr/lib/
	echo "libsnap7.so copied to /ust/lib/libsnap7.so"

else
    echo "Unsupported architecture: $ARCH"
    exit 1
fi

sudo apt-get update
sudo apt-get install python3-tk
pip3 install -r requirements.txt
sudo pip3 install python-snap7

exit 0

