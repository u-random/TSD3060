#!/bin/bash

#Code partly from Thomas Nordli's unshare-container3.sh

# Initialize an unprivileged container environment
# ROOT_FILE_SYSTEM serves as the root file system for the container
# which is expected to be in the path $PWD/../../Distribution

ROOT_FILE_SYSTEM=$PWD/../../Distribution

# Check if the root file system directory exists; if not, create it
if [ ! -d $ROOT_FILE_SYSTEM ]; then

    # Create essential directories bin and proc inside the root file system
    mkdir -p $ROOT_FILE_SYSTEM/{bin,proc}
    
    # Navigate to the bin directory inside the root file system
    cd $ROOT_FILE_SYSTEM/bin/
    
    # Copy busybox (a multi-call binary combining many Unix utilities)
    # from the host system to the new root file system
    cp /bin/busybox .
    
    # Create symbolic links for each utility provided by busybox
    for P in $(./busybox --list); do
        ln -s busybox $P
    done

fi

# Use unshare to set up the container with various isolated namespaces
# Then execute init.sh located in the Scripts/Container directory relative to
# the root file system directory
PATH=/bin \
    unshare \
    --user \
    --map-root-user \
    --fork \
    --pid \
    --mount \
    --cgroup \
    --ipc \
    --uts \
    --net \
    /usr/sbin/chroot $ROOT_FILE_SYSTEM ../Scripts/Container/init.sh


# Manuell inspeksjon i konteineren:
# ----------------------------------
# ps


# Manuell inspeksjon på vertsystemet:
# ----------------------------------
# ps aux | grep /bin/sh       # finner PID
# cat /proc/$PID/{u,g}id_map  # ser kobling mellom bruker-navnerommene


# Debian har deaktivert muligheten for upriviligerte brukere å
# "unshare" bruker-navnerommet. Det kan aktiveres med følgende
# kodelinje:
#
# sudo su -c "echo 1 > /proc/sys/kernel/unprivileged_userns_clone"