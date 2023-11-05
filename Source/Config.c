//
//  Config.c
//  TSD3060-Webserver-1
//
//  Created by Isak Lars Haukeland on 14/09/2023.
//

#include "Config.h"


// MARK: - Private methods


const char *_timestamp(void) {
    static char timestamp[20]; // Enough space for "YYYY-MM-DD HH:MM:SS\0"
    time_t now = time(NULL);
    struct tm *tm_struct = localtime(&now);
    
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", tm_struct);
    return timestamp;
}


// MARK: - Public methods


void Config_openlog(void) {
    char buffer[PATH_MAX] = {};
    // Sets buffer to log file
    snprintf(buffer, PATH_MAX, "%s/var/log/debug.log", Server.distribution_root);
    Server.log = fopen(strdup(buffer), "a");
    if (Server.log == NULL) {
        fprintf(stderr, "Error: Cannot open log file '%s'\n", buffer);
        exit(1);
    }
}


void Config_log(FILE *stream, const char *message, ...) {
    // Variable argument list for message
    va_list ap;
    va_start(ap, message);
    fprintf(stream, "[%s] ", _timestamp());
    vfprintf(stream, message, ap);
    fflush(stream);
    va_end(ap);
}


void Config_error(FILE *stream, const char *error, ...) {
    va_list ap;
    va_start(ap, error);
    fprintf(stream, "[%s] ", _timestamp());
    vfprintf(stream, error, ap);
    fflush(stream);
    va_end(ap);
    _exit(1);
}


void Config_debug(FILE *stream, const char *message, ...) {
    if (Server.debug) {
        va_list ap;
        va_start(ap, message);
        fprintf(stream, "[%s] DEBUG: ", _timestamp());
        vfprintf(stream, message, ap);
        fflush(stream);
        va_end(ap);
    }
}


