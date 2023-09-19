//
//  File.h
//  TSD3060-Webserver-1
//
//  Created by Isak Lars Haukeland on 07/09/2023.
//

#ifndef File_h
#define File_h

bool File_is_asis(const char *path);
bool File_exist(const char *path);
bool File_is_directory(const char *path);
const char *File_mimeType(const char *path);
const char *File_extension(const char *path);
const char *File_basename(const char *path);
const char *File_dirname(char *path);
off_t File_size(const char *path);
void File_writePidFile(void);
void File_removePidFile(void);
pid_t File_readPidFile(void);
#endif /* File_h */
