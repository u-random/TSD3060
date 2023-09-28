//
//  Mime.c
//  TSD3060-Webserver-1
//
//  Created by Isak Lars Haukeland on 08/09/2023.
//

#include "Config.h"

#include "Mime.h"


// MARK: - Definition

#define MAX_MIME_TYPES 2286

// Define a structure for mime type data
typedef struct {
    char *mime_type;
    char *file_extensions;
} MimeEntry;

// Define a structure for the mime table
typedef struct {
    MimeEntry entries[MAX_MIME_TYPES]; // VLA?
    size_t size;
} MimeTable;

// Setup and clear our local mime_table
static MimeTable mime_table = {};


// -------------------------------------------------------------------------------------


// MARK: - Read mime.types file into shared memory hash table
void Mime_initiate(void) {
    char t[PATH_MAX] = {};
    snprintf(t, PATH_MAX, "%s/etc/mime.types", Server.distribution_root);
    FILE *mime_file = fopen(t, "r");
    if (!mime_file) {
        Config_error(stderr, "Failed to open mime.types file");
    }

    // Parse mime.types file and populate the hash table
    char line[512];
    char mime_type[STRLEN];
    char file_extensions[STRLEN];
    while (fgets(line, sizeof(line), mime_file)) {
        if (line[0] == '#' || isspace(line[0]))
            continue;
        if (sscanf(line, "%255s %255[^\n]", mime_type, file_extensions) != 2) {
            continue;
        }
        if (mime_table.size >= MAX_MIME_TYPES) {
            Config_error(stderr, "Too many mime types, increase MAX_MIME_TYPES\n");
        }
        MimeEntry *entry = &mime_table.entries[mime_table.size];
        entry->file_extensions = strdup(file_extensions);
        entry->mime_type = strdup(mime_type);
        mime_table.size++;
    }
    fclose(mime_file);
}


// MARK: - Get current mimetype from request extention
const char *Mime_get(const char* extension) {
    if (STRING_UNDEFINED(extension)) {
        return NULL;
    }

    for (size_t i = 0; i < mime_table.size; i++) {
        MimeEntry entry = mime_table.entries[i];
        // TODO: Don't use substr parsing or improve it as extension "html" matches "xhtml"
        if (strstr(entry.file_extensions, extension)) {
            return entry.mime_type;
        }
    }

    // Return a default mime-type or NULL if not found
    return NULL;
}
