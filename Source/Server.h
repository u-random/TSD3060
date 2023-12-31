//
//  Server.h
//  TSD3060-Webserver-1
//
//  Created by Isak Lars Haukeland on 08/09/2023.
//

#ifndef Server_h
#define Server_h

typedef struct Server_T {
    int bind_port;
    int back_log;
    char *distribution_root; 
    char *web_root;
    char *pid_directory;
    FILE *log;
    int socket_descriptor;
    bool is_daemon;
    bool debug;
    bool stop;
} Server_T;


// Create global Server object
void Server_init(void);

// Start server accept loop
void Server_start(void);

// Stop server accept loop
void Server_stop(void);

#endif /* Server_h */
