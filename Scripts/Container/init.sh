#!/bin/sh

# Mounts proc filesystem. Crucial for processes to interact with kernel.
mount -t proc none /proc
/bin/TSD3060 -r Distribution -p 55556 -i &
exec /bin/sh
