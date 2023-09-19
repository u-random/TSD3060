//
//  File.c
//  TSD3060-Webserver-1
//
//  Created by Isak Lars Haukeland on 07/09/2023.
//
#include "Config.h"
#include "File.h"

// TODO: Remove trailing slashs

bool File_is_asis(const char *path) {
    const char *extention = File_extension(path);
    if (extention)
        return strcasecmp(extention, "asis") == 0;
    return false;
}

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

const char *File_mimeType(const char *path) {
    // TODO: Lookup mimetype based on path extension
    // TODO: If found, set Content-Type header to mime type, otherwise return NULL
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
    snprintf(path, PATH_MAX, "%s/%s.pid", Server.pid_dir, Program_Name);
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
    snprintf(path, PATH_MAX, "%s/%s.pid", Server.pid_dir, Program_Name);
    unlink(path); // Delete pid file
}

pid_t File_readPidFile(void) {
    char path[PATH_MAX];
    // Write path to pid-file by concatinating pid.dir and Program_Name
    snprintf(path, PATH_MAX, "%s/%s.pid", Server.pid_dir, Program_Name);
    FILE *pidFile = fopen(path, "r");
    if (!pidFile)
        Config_error(Server.log, "Could not open pid file '%s'\n", path);
    pid_t pid = -1;
    if (fscanf(pidFile, "%d", &pid) != 1)
        Config_error(Server.log, "Could not read pid from '%s'\n", path);
    fclose(pidFile);
    if (getpgid(pid) > 0 || errno == EPERM) { // Test that the pid actually refer to a running process
            return pid;
    }
    return -1;
}
