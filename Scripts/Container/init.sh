#!/bin/sh
trap 'exit 1' 1 2 15
# Mounts proc filesystem. Crucial for processes to interact with kernel.
mount -t proc none /proc
exec /bin/TSD3060 -r Distribution -p 80 -i 
