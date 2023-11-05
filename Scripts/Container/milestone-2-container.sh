#!/bin/bash

#Code partly from Thomas Nordli's unshare-container3.sh

# Initialize an unprivileged container environment
# ROOT_FILE_SYSTEM serves as the root file system for the container
# which is expected to be in the path $PWD/Distribution

function error() {
        msg=${1?:"need a message"}
        >&2 echo "Error: $msg"
        exit 1
}

ROOT_FILE_SYSTEM=$PWD/tmp
TEMPLATE_FILE_SYSTEM=$PWD/Distribution

# Check if the root file system directory exists; if not, create it
if [ ! -d $ROOT_FILE_SYSTEM ]; then
    
    
    # Makes root file system from distribution template
    cp -a $TEMPLATE_FILE_SYSTEM $ROOT_FILE_SYSTEM || error "Make root file system failed"
    
    cp Scripts/Container/init.sh $ROOT_FILE_SYSTEM/bin || error "cp init failed"

    mkdir -p $ROOT_FILE_SYSTEM/lib/x86_64-linux-gnu/
    cp -a /lib/x86_64-linux-gnu/libc.so.6 $ROOT_FILE_SYSTEM/lib/x86_64-linux-gnu/

    mkdir -p $ROOT_FILE_SYSTEM/lib64/
    cp -a /lib64/ld-linux-x86-64.so.2 $ROOT_FILE_SYSTEM/lib64/

    # Navigate to the bin directory inside the root file system
    cd $ROOT_FILE_SYSTEM/bin/ || error "Could not cd to bin"
    
    # Copy busybox (a multi-call binary combining many Unix utilities)
    # from the host system to the new root file system
    cp /bin/busybox . || error "Could not copy busybox"
    
    # Create symbolic links for each utility provided by busybox
    for P in $(./busybox --list | egrep -v busybox); do
        ln -s busybox $P || error "Linking failed"
    done

fi

exit 1
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
    --mount-proc \
    --root $ROOT_FILE_SYSTEM \
    /bin/TSD3060 -r / -p 80 -i || error "Could not start container"


# Manuell inspeksjon i konteineren:
# ----------------------------------
# ps
#|| error "Could not run unshare"


# Manuell inspeksjon på vertsystemet:
# ----------------------------------
# ps aux | grep /bin/sh       # finner PID
# cat /proc/$PID/{u,g}id_map  # ser kobling mellom bruker-navnerommene


# Debian har deaktivert muligheten for upriviligerte brukere å
# "unshare" bruker-navnerommet. Det kan aktiveres med følgende
# kodelinje:
#
# sudo su -c "echo 1 > /proc/sys/kernel/unprivileged_userns_clone"
