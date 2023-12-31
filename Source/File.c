//
//  File.c
//  TSD3060-Webserver-1
//
//  Created by Isak Lars Haukeland on 07/09/2023.
//
#include "Config.h"
#include "File.h"




bool File_exist(const char *path) {
    if (path) {
        struct stat buf;
        return (stat(path, &buf) == 0);
    }
    return false;
}


bool File_is_directory(const char *path) {
    if (path) {
        struct stat buffer;
        return (stat(path, &buffer) == 0 && S_ISDIR(buffer.st_mode));
    }
    return false;
}


bool File_is_asis(const char *path) {
    const char *extention = File_extension(path);
    if (extention)
        return strcasecmp(extention, "asis") == 0;
    return false;
}

// Returns mimetype if file is in mimetype list, else null.
const char *File_mimeType(const char *path) {
    const char *extension = File_extension(path);

    if (extension) {
        // Use the MIME table to look up the MIME type based on the extension
        const char *mimeType = Mime_get(extension);
        return mimeType;
    }

    // If the extension is not found, return NULL
    return NULL;
}





const char *File_extension(const char *path) {
    if (STRING_DEFINED(path)) {
        char *substring = strrchr(path, '.');
        return (substring ? ++substring : NULL);
    }
    return NULL;
}

const char *File_basename(const char *path) {
        if (STRING_DEFINED(path)) {
                char *f = strrchr(path, '/');
                return (f ? ++f : path);
        }
        return path;
}

const char *File_dirname(char *path) {
    if (STRING_DEFINED(path)) {
        char *d = strrchr(path, '/');
        if (d)
            *(d+1) = '\0'; /* Keep last separator */
        else {
            path[0] = '.';
            path[1] = 0;
        }
    }
    return NULL;
}

off_t File_size(const char *path) {
    if (path) {
        struct stat buf;
        if (stat(path, &buf) < 0)
            return -1;
        return buf.st_size;
    }
    return -1;
}

void File_writePidFile(void) {
    char path[PATH_MAX];
    // Write path to pid-file by concatinating pid.dir and Program_Name
    snprintf(path, PATH_MAX, "%s/%s.pid", Server.pid_directory, Program_Name);
    FILE *pidFile = fopen(path, "w");
    if (!pidFile) {
        Config_error(Server.log, "Could not write pid file '%s'\n", path);
    }
    fprintf(pidFile, "%d\n", getpid());
    fclose(pidFile);
}

void File_removePidFile(void) {
    char path[PATH_MAX];
    // Write path to pid-file by concatinating pid.dir and Program_Name
    snprintf(path, PATH_MAX, "%s/%s.pid", Server.pid_directory, Program_Name);
    unlink(path); // Delete pid file
}

pid_t File_readPidFile(void) {
    char path[PATH_MAX] = {};
    // Write path to pid-file by concatinating pid.dir and Program_Name
    snprintf(path, PATH_MAX, "%s/%s.pid", Server.pid_directory, Program_Name);
    FILE *pidFile = fopen(path, "r");
    if (!pidFile) {
        // pid file does not exist. That's means that the server is not running
        return -1;
    }
    pid_t pid = -1;
    if (fscanf(pidFile, "%d", &pid) != 1)
        Config_error(Server.log, "Could not read pid from '%s'\n", path);
    fclose(pidFile);
    if (getpgid(pid) > 0 || errno == EPERM) { // Test that the pid actually refer to a running process
            return pid;
    }
    return -1;
}

char *File_removeTrailingSlash(char *path) {
    if (STRING_DEFINED(path)){
        size_t path_length = strlen(path);
        if (path[path_length - 1] == '/') {
            // Remove the trailing slash
            path[path_length - 1] = '\0';
        }
    }
    return path;
}
