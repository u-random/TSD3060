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
    printf("  -d dir     Specify document root for server\n");
    printf("  -r dir     Specify directory for pid file\n");
    printf("  -p port    Port number for server\n");
    printf("  -l path    Specify path to logfile\n");
    printf("  -i         Server runs non-daemonized\n");
    printf("  -h         This help text\n");
    printf("Arguments are:\n");
    printf("  start      Start server (default)\n");
    printf("  stop       Stop server\n");
}

// MARK: - Handle arguments

Action_T ArgumentParser_handleArguments(int argc, char **argv) {
    
    int opt;
    opterr = 0;
    while ((opt = getopt(argc, argv, "d:r:p:l:ih")) != -1) { // Required options seperated by colon
        switch (opt) {
            case 'd':
                if (optarg != NULL) {
                    if (!File_is_directory(optarg)) {
                        fprintf(stderr, "Error: document root '%s' does not exist or is not a directory\n", optarg);
                        exit(1);
                    }
                    Server.document_root = optarg;
                } else {
                    fprintf(stderr, "Error: no document root specified\n");
                    exit(1);
                }
                break;
            case 'r':
                if (optarg != NULL) {
                    if (!File_is_directory(optarg)) {
                        fprintf(stderr, "Error: pid-file directory '%s' does not exist or is not a directory\n", optarg);
                        exit(1);
                    }
                    Server.pid_dir = optarg;
                } else {
                    fprintf(stderr, "Error: no pid-file directory specified\n");
                    exit(1);
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
            case 'l':
                if (optarg != NULL) {
                    Server.log = fopen(optarg, "a");
                    if (Server.log == NULL) {
                        fprintf(stderr, "Error: cannot open log file '%s'\n", optarg);
                        exit(1);
                    }
                } else {
                    fprintf(stderr, "Error: no log file specified\n");
                    exit(1);
                }
                break;
            case 'i':
                Server.is_daemon = false;
                break;
            case '?':
                switch(optopt) {
                    case 'd':
                    case 'p':
                    case 'l':
                    case 'r':
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
    
    
    if (optind < argc) { // the optind variable (another global variable set by getopt()) will contain the index of the next argument to be processed. This is used to parse the "start" or "stop" argument.
        if (strcasecmp(argv[optind], "start") == 0) {
            // Check that Required options are set
            if (!Server.document_root)
                Config_error(stderr, "Error: Required option -d document root not set\n");
            if (!Server.pid_dir)
                Config_error(stderr, "Error: Required option -r pid-file not set\n");
            if (!Server.bind_port)
                Config_error(stderr, "Error: Required option -p Port number not set\n");
            if (!Server.log)
                Config_error(stderr, "Error: Required option -l log file not set\n");
            return action_start;
        } else if (strcasecmp(argv[optind], "stop") == 0) {
            // Check that Required options are set
            if (!Server.pid_dir)
                Config_error(stderr, "Error: Please specify argument -r for pid-file to use for quitting\n");
            return action_stop;
        } else { // Here it exits and provides the help if no action command is given
            ArgumentParser_help();
            exit(1);
        }
    }
    
    return action_start; // default action
}
