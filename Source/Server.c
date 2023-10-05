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

#include "File.h"
#include "Http.h"
#include "Server.h"

// MARK: - Global variables

Server_T Server = {};

// MARK: - Private methods

// Change user to the systems www user. If failed, exit
static void change_user(void){
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
    
    if (setgid(gid) != 0) {
        Config_error(Server.log, "setgid failed for '%s'", user);
    }
    if (setuid(uid) != 0) {
        Config_error(Server.log, "setuid failed for '%s'", user);
    }
}

// Daemonize server process - loose controlling terminal and fork twice to avoid creating zombies
static void daemonize(void) {
    pid_t pid;
    umask(0);
    int i;
    int descriptors = getdtablesize(); // Get process file descriptor size
    if ((pid = fork ()) < 0) {
        Config_error(Server.log, "Cannot fork a new Server process\n");
    } else if (pid != 0)
        // Using _exit in case we have atexit handlers, we don't want them called here
        _exit(0);
    setsid(); // loose controlling terminal by becoming a session leader
    signal(SIGHUP, SIG_IGN); // Ensure future opens won't allocate controlling TTYs
    if ((pid = fork ()) < 0) {
        Config_error(Server.log, "Cannot fork a new Server process\n");
    } else if (pid != 0)
        _exit(0);
    if (chdir("/") < 0) { // cd / so we don't prevent any unmount
        Config_error(Server.log, "Cannot chdir to '/'\n");
    }
    // Close all open descriptors and reopen stdio to /dev/null
    for (i = 0; i < descriptors; i++)
        close(i);
    for (i = 0; i < 3; i++) { // Open stdio fds (stdin, stdout, stderr)
        if (open("/dev/null", O_RDWR) != i) {
            Config_error(Server.log, "Cannot open /dev/null\n");
        }
    }
}

// Register a signal handler that is more reliable than signal(3)
static void setupSignalHandler(int signo, void (*func)(int signal)) {
    struct sigaction action;
    action.sa_handler = func;
    sigemptyset(&action.sa_mask);
    action.sa_flags = 0;
    if (sigaction(signo, &action, NULL) < 0) {
        Config_error(Server.log, "sigaction");
    }
}

// Signalhandler for Server.stop
static void do_stop(__attribute__ ((unused)) int sig) {
    Server.stop = true;
}

static void setuptServerSocket(void) {
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
    
    // Connecting socket and local address
    if ( 0 == bind(Server.socket_descriptor, (struct sockaddr *) &local_address, sizeof(local_address)) )
        fprintf(stderr, "Process %d is connected to port %d.\n", getpid(), Server.bind_port);
    else {
        // Errormessage for bind
        Config_error(Server.log, "Could not bind socket");
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
    setupSignalHandler(SIGTERM, do_stop);
    setupSignalHandler(SIGINT, do_stop);
}

void Server_start(void) {
    // Read and setup mime types
    Mime_initiate();
        
    if (Server.is_daemon)
        daemonize();

    fprintf(Server.log, "Starting server with pid: %d\n", getpid());

    File_writePidFile();
    atexit(File_removePidFile); // Remove our pidfile at exit
    setuptServerSocket();
    
    // Waiting for connection request
    listen(Server.socket_descriptor, Server.back_log);
    
    // Use chroot(2) and change root directory to Server.web_root
    if (getuid() == 0) {
        if (chroot(Server.web_root) < 0) {
            Config_error(Server.log, "Cannot chroot to '%s'\n", Server.web_root);
        }
        change_user();
    } else {
        Config_debug(Server.log, "Cannot use chroot as regular user \n");
    }
    
        
    // Loop and accept until we are signaled to stop
    while(!Server.stop) {
        // Accepting recieved request
        int client_socket = accept(Server.socket_descriptor, NULL, NULL);
        if (client_socket < 0) {
            if (Server.stop)
                break;
            continue;
        }
        
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
          
            // Main process pipeline; Read request and write Response
            off_t bytes_written = Http_writeResponse(Http_handleRequest(Http_getRequest(&request, &response)));
            // TODO: Write access Logfile
            fprintf(Server.log, "Bytes written: %lld\n", (long long)bytes_written);
            // Closing socket for read and write
            shutdown(client_socket, SHUT_RDWR);
            // Close socket for reuse by OS
            close(client_socket);
            _exit(0);
        }
    }
    // Shutdown server
    fprintf(Server.log, "Received shutdown signal - closing down..\n");
    fprintf(stdout, "\nReceived shutdown signal - closing down..\n");
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
