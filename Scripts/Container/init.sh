#!/bin/sh
trap 'exit 1' 1 2 15
# Mounts proc filesystem. Crucial for processes to interact with kernel.
mount -t proc none /proc
echo "Hello from init."
ldd /bin/TSD3060
#exec /bin/TSD3060 -r / -p 80 -i
