//
//  Config.c
//  TSD3060-Webserver-1
//
//  Created by Isak Lars Haukeland on 14/09/2023.
//

#include "Config.h"


void Config_error(FILE *stream, const char *error, ...) {
    va_list ap;
    va_start(ap, error);
    vfprintf(stream, error, ap);
    fflush(stream);
    va_end(ap);
    _exit(1);
}


void Config_debug(FILE *stream, const char *message, ...) {
    if (Server.debug) {
        va_list ap;
        va_start(ap, message);
        vfprintf(stream, message, ap);
        fflush(stream);
        va_end(ap);
    }
}

