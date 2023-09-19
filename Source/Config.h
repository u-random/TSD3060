//
//  Config.h
//  TSD3060-Webserver-1
//
//  Created by Isak Lars Haukeland on 04/09/2023.
//

#ifndef Config_h
#define Config_h
#include <stdio.h>
#include <stdbool.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <sys/stat.h>
#include <ctype.h>
#include <sys/time.h>
#include <time.h> // ville ha dette biblioteket for struct tm i Http.c
#include <limits.h>
#include <locale.h>
#include <getopt.h>
#include <stdarg.h>

#include "Server.h"

// MARK: - Globals

extern const char *Program_Name;
extern Server_T Server;                         // Global variable for Server type

#define LOCAL_PORT 55556                        // Port to use. This is no longer in use, as port is passed as startup argument.
#define BACK_LOG 10                             // Que size for waiting requests
#define RFC1123  "%a, %d %b %Y %H:%M:%S GMT"    // RFC1123 date format. See: https://datatracker.ietf.org/doc/html/rfc1123#page-55

// MARK: - Functional macros
// Test if string is empty, returns boolean
#define STRING_DEFINED(string) ((string) && (*string))
// Test if string is not empty, returns boolean
#define STRING_UNDEFINED(string) (!STRING_DEFINED(string))

// MARK: - Functions
// Write an error message and exit
void Config_error(FILE *stream, const char *error, ...);

#endif /* Config_h */
