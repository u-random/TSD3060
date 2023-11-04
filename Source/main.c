//
//  main.c
//  TSD3060-Webserver-1
//
//  Created by Isak Lars Haukeland on 03/09/2023.
//

#include "Config.h"
#include "ArgumentParser.h"
#include "File.h"
#include "Http.h"

// MARK: - Main method

const char *Program_Name;

int main (int argc, char **argv) {
    setlocale(LC_ALL, ""); // Set the locale to ALL, see https://man7.org/linux/man-pages/man3/setlocale.3.html
    Program_Name = File_basename(*argv);
    
    Server_init(); // Setup global Server object
    switch(ArgumentParser_handleArguments(argc, argv)) {
        case action_start:
        {
            pid_t pid = File_readPidFile();
            if (pid > 0) {
                fprintf(stderr, "Server is already running with PID: %d\n", pid);
                exit(1);
            }
            Server_start();
        }
        break;
        case action_stop:
            Server_stop();
            break;
    }

    return 0;
}
