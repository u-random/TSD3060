//
//  Server.c
//  TSD3060-Webserver-1
//
//  Created by Isak Lars Haukeland on 08/09/2023.
//

#include "Config.h"
#include <sys/fcntl.h>
#include <signal.h>
#include <pwd.h>
#ifdef LINUX
#include <sys/wait.h>
#endif

#include "File.h"
#include "Http.h"
#include "Server.h"

// MARK: - Global variables

Server_T Server = {};

// MARK: - Private methods


// Change user to the systems www user. If failed, exit
static void _change_user(void){
#ifndef UNSHARE
    // If we run in a chroot/unshare environment (on Linux)
    // we link the whole server static. The function getpwnam
    // is part of the NSS dynamic module in libc and cannot be
    // easily static linked in this environment. So the change
    // uid/guid functionality is maintained outside from a script
#ifdef DARWIN
    char *user = "www";
#else // Assume Linux
    char *user = "www-data";
#endif
    struct passwd *password_entry = getpwnam(user);
    if (password_entry == NULL) {
        Config_error(Server.log, "getpwnam failed for '%s'", user);
    }
    
    uid_t uid = password_entry->pw_uid;
    gid_t gid = password_entry->pw_gid;
    // Set users groupid
    if (setgid(gid) != 0) {
        Config_error(Server.log, "setgid failed for '%s'", user);
    }
    // Call setuid _after_ setgid before we relinquish any root privileges
    if (setuid(uid) != 0) {
        Config_error(Server.log, "setuid failed for '%s'", user);
    }
#endif
}


// Milestone 1.4: Sett opp Demonisert
// Daemonize server process - loose controlling terminal and fork twice to avoid creating zombies
static void _daemonize(void) {
    pid_t pid;
    umask(0);
    int i;
    int descriptors = getdtablesize(); // Get number of file descriptors for the process
    if ((pid = fork ()) < 0) {
        Config_error(Server.log, "Cannot fork a new Server process\n");
    } else if (pid != 0)
        // Using _exit in case we have atexit handlers, we don't want them called here
        _exit(0);
    // Milestone 1.4: Ingen kontrollterminal
    setsid(); // loose controlling terminal by becoming a session leader
    signal(SIGHUP, SIG_IGN); // Ensure future opens won't allocate controlling TTYs
    if ((pid = fork ()) < 0) {
        Config_error(Server.log, "Cannot fork a new Server process\n");
    } else if (pid != 0)
        _exit(0);
    if (chdir("/") < 0) { // cd / so we don't prevent any unmount
        Config_error(Server.log, "Cannot chdir to '/'\n");
    }
    // Close Server.log here after deamonize, as we close all descriptors below
    fclose(Server.log);
    // Close all open descriptors and reopen stdio to /dev/null
    for (i = 0; i < descriptors; i++) {
        close(i);
    }
    // Open stdio fds (stdin, stdout, stderr)
    bool redirect_error = false;
    for (i = 0; i < 3; i++) {
        if (open("/dev/null", O_RDWR) != i) {
            redirect_error = true;
        }
    }
    // MARK: - Open Server.log again here after deamonize, as daemonize closes all descriptors
    Config_openlog();
    // Failure to redirect stdio file descriptors is an error
    if (redirect_error) {
        Config_error(Server.log, "Error: Could not open standard descriptors to /dev/null\n");
    }
    // Set standard err to logfile.
    // Milestone 1.4: Koble fil til stderr
    stderr = Server.log;
    // Note: If it is required to map stderr fileno to Server.log fileno, use fileno(Server.log) and dup etc
}


// Register a signal handler that is more reliable than signal(3),
// which did not work in this server stop use case after daemonize.
static void _setSignalHandler(int signal_number, void (*signalHandler)(int signal)) {
    // Using sigaction instead of signal.
    struct sigaction action;
    action.sa_handler = signalHandler;
    sigemptyset(&action.sa_mask);
    action.sa_flags = 0;
    if (sigaction(signal_number, &action, NULL) < 0) {
        Config_error(Server.log, "sigaction");
    }
}


// Signalhandler for Server.stop
static void _stopServer(__attribute__ ((unused)) int sig) {
    Server.stop = true;
}


// A simple non-blocking reaper to ensure that we wait-for and reap all/any
// stray child processes we may have created and not waited on, so we do not
// create any zombie processes
static void _waitforchildren(__attribute__ ((unused)) int sig) {
        while (waitpid(-1, NULL, WNOHANG) > 0) ;
}


static void _setupServerSocket(void) {
    // Setting up the socket structure
    Server.socket_descriptor = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    
    // Socket test
    if (Server.socket_descriptor == -1) {
        Config_error(Server.log, "webserver (socket) failed");
    }
    
    printf("Socket created successfully\n");
    
    // So the operating system does not keep port live after server shutdown
    setsockopt(Server.socket_descriptor, SOL_SOCKET, SO_REUSEADDR, &(int){ 1 }, sizeof(int));
    
    // Initiate local address
    struct sockaddr_in local_address = {
        .sin_family      = AF_INET,
        .sin_port        = htons((u_short)Server.bind_port),
        .sin_addr.s_addr = htonl(INADDR_ANY)
    };
    
    // Milestone 1.5: Programmet skal binde seg til porten kun en gang
    // Connecting socket and local address
    if ( 0 == bind(Server.socket_descriptor, (struct sockaddr *) &local_address, sizeof(local_address)) )
        Config_log(Server.log, "Process %d is connected to port %d.\n", getpid(), Server.bind_port);
    else {
        // Errormessage for bind
        Config_error(Server.log, "Could not bind socket\n");
    }
}

// MARK: - Public methods

void Server_init(void) {
    Server = (Server_T) {
        .bind_port = LOCAL_PORT,
        .back_log = BACK_LOG,
        .is_daemon = true
    };
    // Setup a signal handler for handling server stop
    _setSignalHandler(SIGTERM, _stopServer);
    _setSignalHandler(SIGINT, _stopServer);
    // Setup a signal handler for CHILD process exit
    // which reaps them
    _setSignalHandler(SIGCHLD, _waitforchildren);
}


void Server_start(void) {
    // Read and setup mime types
    Mime_initiate();
        
    // Milestone 1.4: Kjør demonisert
    if (Server.is_daemon)
        _daemonize();
    
    fprintf(Server.log, "\n");
    Config_log(Server.log, "Starting server with pid: %d\n", getpid());

    File_writePidFile();
    atexit(File_removePidFile); // Remove our pidfile at exit
    _setupServerSocket();
    
    // Waiting for connection request
    listen(Server.socket_descriptor, Server.back_log);
    Config_debug(Server.log, "Successfully listen on port %d\n", Server.socket_descriptor);

    // Use chroot(2) and change root directory to Server.web_root
    if (getuid() == 0) {
        // Milestone 1.6: Endre serverens root til web-root
        if (chroot(Server.web_root) < 0) {
            Config_error(Server.log, "Cannot chroot to '%s'\n", Server.web_root);
        } else {
            Config_debug(Server.log, "Successfully chroot to %s\n", Server.web_root);
            // Need to modify web_root to '/'
            strncpy(Server.web_root, "/", sizeof("/"));
        }
        // Change the user to www user to drop privileges, if any
        _change_user();
    } else {
        Config_log(Server.log, "Warning: Cannot use chroot as regular user \n");
    }
    
    // Loop and accept until we are signaled to stop
    while(!Server.stop) {
        // Accepting recieved request. Hangs here waiting for client connection.
        Config_debug(Server.log, "About to accept connection\n");
        int client_socket = accept(Server.socket_descriptor, NULL, NULL);
        if (client_socket < 0) {
            if (Server.stop)
                break;
            continue;
        } else {
            Config_debug(Server.log, "Accepted client connection (%d)\n", client_socket);
        }
        
        // Milestone 1.3: Hver forespørsel skal bli behandlet i egen prosess
        pid_t pid = fork();
        
        if (pid == 0) { // Child Process
            struct Response_T response = {
                .http_status = SC_OK,
                .output_stream = fdopen(client_socket, "w")
            };
            struct Request_T request = {
                .response = &response,  // Associate response with request
                .socket_descriptor = client_socket,
                .input_stream = fdopen(client_socket, "r")
            };
            Config_debug(Server.log, "Start Handling request in child\n");
            // Main process pipeline; Read request and write Response
            off_t bytes_written = Http_writeResponse(Http_handleRequest(Http_getRequest(&request, &response)));
            // Write access Logfile
            Config_log(Server.log, "%s - %i - %lld\n", request.file_path, response.http_status, (long long)bytes_written);
            // Closing socket for read and write
            shutdown(client_socket, SHUT_RDWR);
            // Close socket for reuse by OS
            close(client_socket);
            _exit(0);
        }

    } // end while
    // Shutdown server
    Config_log(Server.log, "Received shutdown signal - closing down..\n");
    Config_log(stdout, "\nReceived shutdown signal - closing down..\n");
    shutdown(Server.socket_descriptor, SHUT_RDWR);
    if(Server.log) {
        fclose(Server.log);
    }
    close(Server.socket_descriptor);
    exit(0);
}


void Server_stop(void) {
    pid_t pid = File_readPidFile();
    if (pid < 0)
        Config_error(stderr, "Error: Could not read pid\n");
    // Signal server to stop
    kill(pid, SIGTERM);
}
