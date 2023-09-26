//
//  ArgumentParser.c
//  TSD3060-Webserver-1
//
//  Created by Isak Haukeland on 11/09/2023.
//

#include "Config.h"
#include "File.h"
#include "ArgumentParser.h"

// MARK: - Help

void ArgumentParser_help(void) {
    printf("Usage: %s [options] {arguments}\n", Program_Name);
    printf("Options are as follows:\n");
    printf("  -r dir     Specify distribution root for server\n");
    printf("  -p port    Port number for server\n");
    printf("  -d         Print debug info\n");
    printf("  -i         Server runs non-daemonized\n");
    printf("  -v         Print Version information\n");
    printf("  -h         This help text\n");
    printf("Arguments are:\n");
    printf("  start      Start server (default)\n");
    printf("  stop       Stop server\n");
}

// MARK: - Handle arguments

Action_T ArgumentParser_handleArguments(int argc, char **argv) {
    
    int opt;
    opterr = 0;
    char buffer[PATH_MAX] = {};
    char distribution_root[PATH_MAX] = {}; // Transient
    
    while ((opt = getopt(argc, argv, "r:p:divh")) != -1) { // Required options seperated by colon
        switch (opt) {
            case 'r':
                if (optarg != NULL) {
                    // MARK: - Write real path for optarg to distribution_root
                    realpath(optarg, distribution_root);
                    if (!File_is_directory(distribution_root)) {
                        fprintf(stderr, "Error: Distribution root '%s' does not exist or is not a directory\n", optarg);
                        exit(1);
                    }
                    
                    // MARK: - Test web root
                    // Sets buffer to web root
                    snprintf(buffer, PATH_MAX, "%s/var/www", distribution_root);
                    if (!File_is_directory(buffer)) {
                        fprintf(stderr, "Error: Web root '%s' does not exist or is not a directory\n", buffer);
                        exit(1);
                    }
                    // Sets distribution root to buffer
                    Server.web_root = strdup(buffer);
                    
                    // MARK: - Test and Setup pid_directory
                    // Sets buffer to run path
                    snprintf(buffer, PATH_MAX, "%s/var/run", distribution_root);
                    if (!File_is_directory(buffer)) {
                        fprintf(stderr, "Error: Given PID directory: '%s' does not exist or is not a directory\n", buffer);
                        exit(1);
                    }
                    // Sets run directory to buffer
                    Server.pid_directory = strdup(buffer);
                                        
                    // MARK: - Test and open log file
                    // Sets buffer to log path
                    snprintf(buffer, PATH_MAX, "%s/var/log", distribution_root);
                    if (!File_is_directory(buffer)) {
                        fprintf(stderr, "Error: Log directory '%s' does not exist or is not a directory\n", buffer);
                        exit(1);
                    }
                    // Sets buffer to log file
                    snprintf(buffer, PATH_MAX, "%s/var/log/debug.log", distribution_root);
                    Server.log = fopen(strdup(buffer), "a");
                    if (Server.log == NULL) {
                        fprintf(stderr, "Error: Cannot open log file '%s'\n", optarg);
                        exit(1);
                    }
                }
                break;
            case 'p':
                if (optarg != NULL) { // Test if port argument is given
                    int port_number = atoi(optarg); // convert string to int
                    if (port_number == 0 && strcmp(optarg, "0") != 0) {
                        fprintf(stderr, "Error: port '%s' is not a valid integer\n", optarg);
                        exit(1);
                    }
                    Server.bind_port = port_number;
                } else {
                    fprintf(stderr, "Error: no port specified\n");
                    exit(1);
                }
                break;
            case 'i':
                Server.is_daemon = false;
                break;
            case 'd':
                Server.debug = true;
                break;
            case 'v':
                printf("%s version 1.0\n", Program_Name);
                break;
            case '?':
                switch(optopt) {
                    case 'r':
                    case 'p':
                    {
                        fprintf(stderr, "%s: option %c -- requires an argument\n", Program_Name, optopt);
                        break;
                    }
                    default:
                    {
                        fprintf(stderr, "%s: invalid option -- %c (-h will show valid options)\n", Program_Name, optopt);
                    }
                }
                exit(1);
                break;
            case 'h':
                // Fall-through
            default:
                ArgumentParser_help();
                exit(1);
        }
    }
    
    // MARK: - Check that Required options are set
    if (STRING_UNDEFINED(distribution_root))
        Config_error(stderr, "Error: Required option -r distribution root not set\n");
    
    // MARK: - What that is done at start parameter
    if (optind < argc) {
        if (strcasecmp(argv[optind], "start") == 0) {
            // Empty
        } else if (strcasecmp(argv[optind], "stop") == 0) {
            return action_stop;
        } else {
            Config_error(stderr, "Error: Unknown argument '%s'\n", argv[optind]);
        }
    }
    // Default action is start
    if (Server.bind_port <= 0)
        Config_error(stderr, "Error: Required option -p Port number not set\n");
    return action_start;
}
